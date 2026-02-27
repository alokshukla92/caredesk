import json
import logging
from datetime import date
from utils.constants import (
    TABLE_CLINICS, TABLE_DOCTORS, TABLE_APPOINTMENTS, TABLE_PATIENTS,
    STATUS_BOOKED, STATUS_IN_QUEUE,
)
from utils.response import success, created, error, not_found, server_error
from services.zia_service import analyze_sentiment, extract_keywords
from services.cache_service import get_queue_state
from services.signals_service import emit_appointment_event

logger = logging.getLogger(__name__)


def _get_clinic_by_slug(app, slug):
    """Look up a clinic by its URL slug."""
    zcql = app.zcql()
    result = zcql.execute_query(
        f"SELECT ROWID, name, slug, address, phone, email, logo_url "
        f"FROM {TABLE_CLINICS} WHERE slug = '{slug}'"
    )
    if result and len(result) > 0:
        return result[0][TABLE_CLINICS]
    return None


def get_clinic(app, request, slug):
    """GET /api/public/clinic/:slug — Public clinic info + doctors."""
    try:
        clinic = _get_clinic_by_slug(app, slug)
        if not clinic:
            return not_found("Clinic not found")

        clinic_id = clinic["ROWID"]

        # Get active doctors
        zcql = app.zcql()
        doctors_result = zcql.execute_query(
            f"SELECT ROWID, name, specialty, available_from, available_to, consultation_fee "
            f"FROM {TABLE_DOCTORS} "
            f"WHERE clinic_id = '{clinic_id}' AND status = 'active' "
            f"ORDER BY name ASC"
        )

        doctors = []
        for row in (doctors_result or []):
            d = row[TABLE_DOCTORS]
            doctors.append({
                "id": d["ROWID"],
                "name": d["name"],
                "specialty": d["specialty"],
                "available_from": d["available_from"],
                "available_to": d["available_to"],
                "consultation_fee": d["consultation_fee"],
            })

        return success({
            "clinic": {
                "id": clinic_id,
                "name": clinic["name"],
                "slug": clinic["slug"],
                "address": clinic["address"],
                "phone": clinic["phone"],
                "email": clinic["email"],
                "logo_url": clinic["logo_url"],
            },
            "doctors": doctors,
        })

    except Exception as e:
        logger.error(f"Public get clinic error: {e}")
        return server_error(str(e))


def book_appointment(app, request):
    """POST /api/public/book — Patient self-service booking."""
    try:
        body = request.get_json(silent=True) or {}
        slug = body.get("clinic_slug", "").strip()
        doctor_id = body.get("doctor_id", "").strip()
        patient_name = body.get("patient_name", "").strip()
        patient_phone = body.get("patient_phone", "").strip()
        patient_email = body.get("patient_email", "").strip()
        appt_date = body.get("appointment_date", date.today().isoformat())
        appt_time = body.get("appointment_time", "")

        if not slug or not doctor_id or not patient_name or not patient_phone:
            return error("Clinic, doctor, patient name and phone are required")

        clinic = _get_clinic_by_slug(app, slug)
        if not clinic:
            return not_found("Clinic not found")

        clinic_id = clinic["ROWID"]
        zcql = app.zcql()

        # Find or create patient
        patient_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND phone = '{patient_phone}'"
        )

        if patient_result and len(patient_result) > 0:
            patient_id = patient_result[0][TABLE_PATIENTS]["ROWID"]
        else:
            patient_table = app.datastore().table(TABLE_PATIENTS)
            patient_row = patient_table.insert_row({
                "clinic_id": clinic_id,
                "name": patient_name,
                "phone": patient_phone,
                "email": patient_email,
                "age": body.get("age", ""),
                "gender": body.get("gender", ""),
                "blood_group": "",
                "medical_history": "",
            })
            patient_id = patient_row["ROWID"]

        # Generate token
        token_result = zcql.execute_query(
            f"SELECT token_number FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{appt_date}' "
            f"ORDER BY ROWID DESC LIMIT 1"
        )
        if token_result and len(token_result) > 0:
            last_token = token_result[0][TABLE_APPOINTMENTS].get("token_number", "T-000")
            try:
                num = int(last_token.split("-")[1])
            except (IndexError, ValueError):
                num = 0
            token = f"T-{str(num + 1).zfill(3)}"
        else:
            token = "T-001"

        # Create appointment
        appt_table = app.datastore().table(TABLE_APPOINTMENTS)
        row = appt_table.insert_row({
            "clinic_id": clinic_id,
            "doctor_id": doctor_id,
            "patient_id": str(patient_id),
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "status": STATUS_BOOKED,
            "token_number": token,
            "notes": body.get("notes", ""),
            "feedback_score": "",
            "feedback_text": "",
            "feedback_sentiment": "",
        })

        return created({
            "appointment_id": row["ROWID"],
            "token_number": token,
            "status": STATUS_BOOKED,
            "clinic_name": clinic["name"],
            "appointment_date": appt_date,
            "appointment_time": appt_time,
        }, "Appointment booked! Please note your token number.")

    except Exception as e:
        logger.error(f"Public booking error: {e}")
        return server_error(str(e))


def get_queue(app, request, slug):
    """GET /api/public/queue/:slug — Public live queue display."""
    try:
        clinic = _get_clinic_by_slug(app, slug)
        if not clinic:
            return not_found("Clinic not found")

        clinic_id = clinic["ROWID"]
        today = date.today().isoformat()

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.token_number, "
            f"{TABLE_APPOINTMENTS}.status, {TABLE_APPOINTMENTS}.doctor_id, "
            f"{TABLE_DOCTORS}.name "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.appointment_date = '{today}' "
            f"AND {TABLE_APPOINTMENTS}.status IN ('{STATUS_IN_QUEUE}', 'in-consultation') "
            f"ORDER BY {TABLE_APPOINTMENTS}.token_number ASC"
        )

        queue = []
        now_serving = []
        waiting = []

        for row in (result or []):
            a = row[TABLE_APPOINTMENTS]
            entry = {
                "token_number": a["token_number"],
                "status": a["status"],
                "doctor_name": row.get(TABLE_DOCTORS, {}).get("name", ""),
            }
            if a["status"] == "in-consultation":
                now_serving.append(entry)
            else:
                waiting.append(entry)

        return success({
            "clinic_name": clinic["name"],
            "date": today,
            "now_serving": now_serving,
            "waiting": waiting,
            "total_waiting": len(waiting),
        })

    except Exception as e:
        logger.error(f"Public queue error: {e}")
        return server_error(str(e))


def submit_feedback(app, request, appointment_id):
    """POST /api/public/feedback/:appointment_id — Submit patient feedback."""
    try:
        body = request.get_json(silent=True) or {}
        score = body.get("score", "")
        feedback_text = body.get("feedback_text", "").strip()

        if not score:
            return error("Feedback score is required")

        # Analyze sentiment and extract keywords using Zia
        sentiment = "neutral"
        keywords = []
        if feedback_text:
            sentiment = analyze_sentiment(app, feedback_text)
            keywords = extract_keywords(app, feedback_text)

        table = app.datastore().table(TABLE_APPOINTMENTS)
        table.update_row({
            "ROWID": appointment_id,
            "feedback_score": str(score),
            "feedback_text": feedback_text,
            "feedback_sentiment": sentiment,
        })

        # Emit signal for real-time dashboard updates
        emit_appointment_event(app, "", "feedback_received", {
            "appointment_id": appointment_id,
            "score": score,
            "sentiment": sentiment,
        })

        return success({
            "appointment_id": appointment_id,
            "score": score,
            "sentiment": sentiment,
            "keywords": keywords,
        }, "Thank you for your feedback!")

    except Exception as e:
        logger.error(f"Submit feedback error: {e}")
        return server_error(str(e))
