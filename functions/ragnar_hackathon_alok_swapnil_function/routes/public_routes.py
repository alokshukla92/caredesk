import json
import logging
from utils.constants import (
    TABLE_CLINICS, TABLE_DOCTORS, TABLE_APPOINTMENTS, TABLE_PATIENTS,
    TABLE_PRESCRIPTIONS, STATUS_BOOKED, STATUS_IN_QUEUE,
    ist_today, ist_time_now,
)
from utils.response import success, created, error, not_found, server_error
from services.zia_service import analyze_sentiment, extract_keywords
from services.cache_service import get_queue_state
from services.signals_service import emit_appointment_event
from services.sms_service import send_booking_sms
from services.mail_service import send_appointment_confirmation

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


def list_clinics(app, request):
    """GET /api/public/clinics — List all clinics for public directory."""
    try:
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, slug, address, phone, email, logo_url "
            f"FROM {TABLE_CLINICS} ORDER BY name ASC"
        )

        clinics = []
        for row in (result or []):
            c = row[TABLE_CLINICS]
            # Count active doctors for each clinic
            doc_count = zcql.execute_query(
                f"SELECT ROWID FROM {TABLE_DOCTORS} "
                f"WHERE clinic_id = '{c['ROWID']}' AND status = 'active'"
            )
            clinics.append({
                "id": c["ROWID"],
                "name": c["name"],
                "slug": c["slug"],
                "address": c["address"],
                "phone": c["phone"],
                "email": c["email"],
                "logo_url": c.get("logo_url", ""),
                "doctor_count": len(doc_count) if doc_count else 0,
            })

        return success(clinics)

    except Exception as e:
        logger.error(f"List clinics error: {e}")
        return server_error(str(e))


def my_appointments(app, request):
    """POST /api/public/my-appointments — Lookup appointments by phone."""
    try:
        body = request.get_json(silent=True) or {}
        phone = body.get("phone", "").strip()

        if not phone:
            return error("Phone number is required")

        zcql = app.zcql()

        # Find patient by phone (could be in multiple clinics)
        patient_result = zcql.execute_query(
            f"SELECT ROWID, clinic_id, name FROM {TABLE_PATIENTS} "
            f"WHERE phone = '{phone}'"
        )
        if not patient_result or len(patient_result) == 0:
            return success([])

        all_appointments = []
        for pat_row in patient_result:
            p = pat_row[TABLE_PATIENTS]
            patient_id = p["ROWID"]
            clinic_id = p["clinic_id"]

            # Get clinic name
            clinic_res = zcql.execute_query(
                f"SELECT name, slug FROM {TABLE_CLINICS} WHERE ROWID = '{clinic_id}'"
            )
            clinic_name = clinic_res[0][TABLE_CLINICS]["name"] if clinic_res else ""
            clinic_slug = clinic_res[0][TABLE_CLINICS]["slug"] if clinic_res else ""

            # Get appointments for this patient
            appt_result = zcql.execute_query(
                f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.appointment_date, "
                f"{TABLE_APPOINTMENTS}.appointment_time, {TABLE_APPOINTMENTS}.status, "
                f"{TABLE_APPOINTMENTS}.token_number, {TABLE_APPOINTMENTS}.feedback_score, "
                f"{TABLE_DOCTORS}.name "
                f"FROM {TABLE_APPOINTMENTS} "
                f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
                f"WHERE {TABLE_APPOINTMENTS}.patient_id = '{patient_id}' "
                f"AND {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
                f"ORDER BY {TABLE_APPOINTMENTS}.appointment_date DESC, "
                f"{TABLE_APPOINTMENTS}.appointment_time DESC"
            )

            for row in (appt_result or []):
                a = row[TABLE_APPOINTMENTS]
                d = row.get(TABLE_DOCTORS, {})

                # Check if prescription exists for completed appointments
                has_prescription = False
                prescription_id = ""
                if a["status"] == "completed":
                    rx = zcql.execute_query(
                        f"SELECT ROWID FROM {TABLE_PRESCRIPTIONS} "
                        f"WHERE appointment_id = '{a['ROWID']}'"
                    )
                    if rx and len(rx) > 0:
                        has_prescription = True
                        prescription_id = rx[0][TABLE_PRESCRIPTIONS]["ROWID"]

                all_appointments.append({
                    "id": a["ROWID"],
                    "clinic_name": clinic_name,
                    "clinic_slug": clinic_slug,
                    "doctor_name": d.get("name", ""),
                    "appointment_date": a["appointment_date"],
                    "appointment_time": a["appointment_time"],
                    "status": a["status"],
                    "token_number": a["token_number"],
                    "feedback_score": a.get("feedback_score", ""),
                    "has_prescription": has_prescription,
                    "prescription_id": prescription_id,
                })

        return success(all_appointments)

    except Exception as e:
        logger.error(f"My appointments error: {e}")
        return server_error(str(e))


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
        appt_date = body.get("appointment_date", ist_today())
        appt_time = body.get("appointment_time", "")

        if not slug or not doctor_id or not patient_name or not patient_phone:
            return error("Clinic, doctor, patient name and phone are required")

        clinic = _get_clinic_by_slug(app, slug)
        if not clinic:
            return not_found("Clinic not found")

        clinic_id = clinic["ROWID"]
        zcql = app.zcql()

        # Validate: appointment time is required
        if not appt_time:
            return error("Appointment time is required. Please select a time slot.")

        # Validate: cannot book in the past
        today_str = ist_today()
        if appt_date < today_str:
            return error("Cannot book appointment for a past date. Please select today or a future date.")

        # Validate: same-day past time check
        if appt_date == today_str and appt_time:
            now = ist_time_now()
            if appt_time <= now:
                return error("Selected time has already passed. Please choose a later time for today's appointment.")

        # Validate: doctor exists, belongs to this clinic, and is active
        doc_check = zcql.execute_query(
            f"SELECT ROWID, status, available_from, available_to, name FROM {TABLE_DOCTORS} "
            f"WHERE ROWID = '{doctor_id}' AND clinic_id = '{clinic_id}'"
        )
        if not doc_check or len(doc_check) == 0:
            return error("Doctor not found in this clinic.")
        doc = doc_check[0][TABLE_DOCTORS]
        if doc.get("status") == "inactive":
            return error(f"Dr. {doc.get('name', '')} is currently unavailable. Please choose another doctor.")

        # Validate: appointment time is within doctor's available hours
        avail_from = doc.get("available_from", "")
        avail_to = doc.get("available_to", "")
        if avail_from and avail_to and appt_time:
            if appt_time < avail_from or appt_time > avail_to:
                return error(
                    f"Dr. {doc.get('name', '')} is available only from {avail_from} to {avail_to}. "
                    f"Please select a time within these hours."
                )

        # Validate: no duplicate booking for same doctor at same date+time
        conflict = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND doctor_id = '{doctor_id}' "
            f"AND appointment_date = '{appt_date}' AND appointment_time = '{appt_time}' "
            f"AND status != 'cancelled'"
        )
        if conflict and len(conflict) > 0:
            return error("This time slot is already booked. Please choose a different time.")

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

        # Generate token with doctor initials
        from routes.appointment_routes import _generate_token
        token = _generate_token(app, clinic_id, appt_date, doc.get("name", ""))

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

        # Send booking confirmation email
        try:
            if patient_email:
                send_appointment_confirmation(
                    app, patient_email, patient_name, doc.get("name", ""),
                    clinic["name"], appt_date, appt_time, token
                )
        except Exception as mail_err:
            logger.warning(f"Confirmation mail failed (non-critical): {mail_err}")

        # Send booking confirmation SMS
        try:
            if patient_phone:
                send_booking_sms(
                    patient_phone, patient_name, doc.get("name", ""),
                    token, appt_time, appt_date, clinic["name"]
                )
        except Exception as sms_err:
            logger.warning(f"SMS send failed (non-critical): {sms_err}")

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
        today = ist_today()

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

        # Validate score is a number between 1 and 5
        try:
            score_val = int(score)
            if score_val < 1 or score_val > 5:
                return error("Score must be between 1 and 5")
        except (ValueError, TypeError):
            return error("Score must be a number between 1 and 5")

        # Validate: appointment exists and is completed
        zcql = app.zcql()
        appt_check = zcql.execute_query(
            f"SELECT ROWID, status, feedback_score FROM {TABLE_APPOINTMENTS} "
            f"WHERE ROWID = '{appointment_id}'"
        )
        if not appt_check or len(appt_check) == 0:
            return not_found("Appointment not found")
        appt = appt_check[0][TABLE_APPOINTMENTS]
        if appt["status"] != "completed":
            return error("Feedback can only be submitted for completed appointments")
        if appt.get("feedback_score", ""):
            return error("Feedback has already been submitted for this appointment")

        # Analyze sentiment and extract keywords using Zia
        sentiment = "neutral"
        keywords = []
        if feedback_text:
            sentiment = analyze_sentiment(app, feedback_text)
            keywords = extract_keywords(app, feedback_text)

        keywords_str = ",".join(keywords) if keywords else ""

        table = app.datastore().table(TABLE_APPOINTMENTS)
        table.update_row({
            "ROWID": appointment_id,
            "feedback_score": str(score),
            "feedback_text": feedback_text,
            "feedback_sentiment": sentiment,
            "feedback_keywords": keywords_str,
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


def get_prescription(app, request, prescription_id):
    """GET /api/public/prescription/:id — Public prescription view (no auth)."""
    try:
        zcql = app.zcql()

        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.clinic_id, "
            f"{TABLE_PRESCRIPTIONS}.appointment_id, {TABLE_PRESCRIPTIONS}.diagnosis, "
            f"{TABLE_PRESCRIPTIONS}.medicines, {TABLE_PRESCRIPTIONS}.advice, "
            f"{TABLE_PRESCRIPTIONS}.follow_up_date, {TABLE_PRESCRIPTIONS}.CREATEDTIME, "
            f"{TABLE_DOCTORS}.name, {TABLE_DOCTORS}.specialty, "
            f"{TABLE_PATIENTS}.name, {TABLE_PATIENTS}.age, {TABLE_PATIENTS}.gender "
            f"FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_PRESCRIPTIONS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_PRESCRIPTIONS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.ROWID = '{prescription_id}'"
        )

        if not result or len(result) == 0:
            return not_found("Prescription not found")

        rx = result[0][TABLE_PRESCRIPTIONS]
        d = result[0].get(TABLE_DOCTORS, {})
        p = result[0].get(TABLE_PATIENTS, {})

        # Get clinic info
        clinic_res = zcql.execute_query(
            f"SELECT name, address, phone FROM {TABLE_CLINICS} "
            f"WHERE ROWID = '{rx['clinic_id']}'"
        )
        clinic_data = clinic_res[0][TABLE_CLINICS] if clinic_res else {}

        medicines = rx["medicines"]
        try:
            medicines = json.loads(medicines)
        except (json.JSONDecodeError, TypeError):
            medicines = []

        return success({
            "id": rx["ROWID"],
            "clinic_name": clinic_data.get("name", ""),
            "clinic_address": clinic_data.get("address", ""),
            "clinic_phone": clinic_data.get("phone", ""),
            "doctor_name": d.get("name", ""),
            "doctor_specialty": d.get("specialty", ""),
            "patient_name": p.get("name", ""),
            "patient_age": p.get("age", ""),
            "patient_gender": p.get("gender", ""),
            "diagnosis": rx["diagnosis"],
            "medicines": medicines,
            "advice": rx["advice"],
            "follow_up_date": rx["follow_up_date"],
            "created_time": rx["CREATEDTIME"],
        })

    except Exception as e:
        logger.error(f"Public prescription view error: {e}")
        return server_error(str(e))
