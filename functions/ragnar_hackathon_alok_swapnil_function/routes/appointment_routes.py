import logging
from utils.constants import (
    TABLE_APPOINTMENTS, TABLE_DOCTORS, TABLE_PATIENTS,
    STATUS_BOOKED, STATUS_IN_QUEUE, STATUS_TRANSITIONS, VALID_STATUSES,
    ist_today, ist_time_now,
)
from utils.response import success, created, error, not_found, server_error
from services.auth_service import require_clinic
from services.cache_service import set_queue_state
from services.mail_service import send_appointment_confirmation
from services.signals_service import emit_queue_update, emit_appointment_event
from services.sms_service import send_booking_sms

logger = logging.getLogger(__name__)


def _get_doctor_initials(doctor_name):
    """Get initials from doctor name. 'Alok Shukla' -> 'AS'."""
    parts = doctor_name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    if parts:
        return parts[0][:2].upper()
    return "DR"


def _generate_token(app, clinic_id, appointment_date, doctor_name=""):
    """Generate next token number for the clinic on given date, using doctor initials."""
    prefix = _get_doctor_initials(doctor_name) if doctor_name else "T"
    try:
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT token_number FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{appointment_date}'"
        )
        max_num = 0
        for row in (result or []):
            token = row[TABLE_APPOINTMENTS].get("token_number", "")
            try:
                num = int(token.split("-")[1])
                if num > max_num:
                    max_num = num
            except (IndexError, ValueError):
                pass
        return f"{prefix}-{str(max_num + 1).zfill(3)}"
    except Exception:
        return f"{prefix}-001"


def list_today(app, request):
    """GET /api/appointments — List today's appointments."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        today = ist_today()
        filter_date = request.args.get("date", today)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.doctor_id, "
            f"{TABLE_APPOINTMENTS}.patient_id, {TABLE_APPOINTMENTS}.appointment_date, "
            f"{TABLE_APPOINTMENTS}.appointment_time, {TABLE_APPOINTMENTS}.status, "
            f"{TABLE_APPOINTMENTS}.token_number, {TABLE_APPOINTMENTS}.notes, "
            f"{TABLE_APPOINTMENTS}.feedback_score, {TABLE_APPOINTMENTS}.feedback_text, "
            f"{TABLE_APPOINTMENTS}.feedback_sentiment, "
            f"{TABLE_DOCTORS}.name, {TABLE_PATIENTS}.name, {TABLE_PATIENTS}.phone "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_APPOINTMENTS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.appointment_date = '{filter_date}' "
            f"ORDER BY {TABLE_APPOINTMENTS}.appointment_time ASC"
        )

        appointments = []
        for row in (result or []):
            a = row[TABLE_APPOINTMENTS]
            d = row.get(TABLE_DOCTORS, {})
            p = row.get(TABLE_PATIENTS, {})
            appointments.append({
                "id": a["ROWID"],
                "doctor_id": a["doctor_id"],
                "doctor_name": d.get("name", ""),
                "patient_id": a["patient_id"],
                "patient_name": p.get("name", ""),
                "patient_phone": p.get("phone", ""),
                "appointment_date": a["appointment_date"],
                "appointment_time": a["appointment_time"],
                "status": a["status"],
                "token_number": a["token_number"],
                "notes": a["notes"],
                "feedback_score": a.get("feedback_score", ""),
                "feedback_text": a.get("feedback_text", ""),
                "feedback_sentiment": a.get("feedback_sentiment", ""),
            })

        return success(appointments)

    except Exception as e:
        logger.error(f"List appointments error: {e}")
        return server_error(str(e))


def create(app, request):
    """POST /api/appointments — Book a new appointment."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        body = request.get_json(silent=True) or {}
        doctor_id = body.get("doctor_id", "").strip()
        patient_id = body.get("patient_id", "").strip()
        appt_date = body.get("appointment_date", ist_today())
        appt_time = body.get("appointment_time", "")

        if not doctor_id or not patient_id:
            return error("Doctor and patient are required")

        if not appt_time:
            return error("Appointment time is required. Please select a time slot.")

        zcql = app.zcql()

        # Validate: appointment date is not in the past
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
            return error(f"Dr. {doc.get('name', '')} is currently inactive. Please choose another doctor.")

        # Validate: appointment time is within doctor's available hours
        avail_from = doc.get("available_from", "")
        avail_to = doc.get("available_to", "")
        if avail_from and avail_to and appt_time:
            if appt_time < avail_from or appt_time > avail_to:
                return error(
                    f"Dr. {doc.get('name', '')} is available only from {avail_from} to {avail_to}. "
                    f"Please select a time within these hours."
                )

        # Validate: patient exists and belongs to this clinic
        pat_check = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} "
            f"WHERE ROWID = '{patient_id}' AND clinic_id = '{clinic_id}'"
        )
        if not pat_check or len(pat_check) == 0:
            return error("Patient not found in this clinic")

        # Validate: no duplicate booking for same doctor at same date+time
        conflict = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND doctor_id = '{doctor_id}' "
            f"AND appointment_date = '{appt_date}' AND appointment_time = '{appt_time}' "
            f"AND status != 'cancelled'"
        )
        if conflict and len(conflict) > 0:
            return error("This doctor already has an appointment at this time")

        token = _generate_token(app, clinic_id, appt_date, doc.get("name", ""))

        table = app.datastore().table(TABLE_APPOINTMENTS)
        row = table.insert_row({
            "clinic_id": clinic_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "status": STATUS_BOOKED,
            "token_number": token,
            "notes": body.get("notes", ""),
            "feedback_score": "",
            "feedback_text": "",
            "feedback_sentiment": "",
        })

        # Try to send confirmation email (non-blocking)
        try:
            zcql = app.zcql()
            patient_res = zcql.execute_query(
                f"SELECT name, email FROM {TABLE_PATIENTS} WHERE ROWID = '{patient_id}'"
            )
            doctor_res = zcql.execute_query(
                f"SELECT name FROM {TABLE_DOCTORS} WHERE ROWID = '{doctor_id}'"
            )
            clinic_res = zcql.execute_query(
                f"SELECT name FROM Clinics WHERE ROWID = '{clinic_id}'"
            )
            if patient_res and doctor_res and clinic_res:
                p_email = patient_res[0][TABLE_PATIENTS].get("email", "")
                if p_email:
                    send_appointment_confirmation(
                        app,
                        patient_email=p_email,
                        patient_name=patient_res[0][TABLE_PATIENTS]["name"],
                        doctor_name=doctor_res[0][TABLE_DOCTORS]["name"],
                        clinic_name=clinic_res[0]["Clinics"]["name"],
                        appointment_date=appt_date,
                        appointment_time=appt_time,
                        token_number=token,
                    )
        except Exception as mail_err:
            logger.warning(f"Mail send failed (non-critical): {mail_err}")

        # Send booking confirmation SMS
        try:
            if patient_res:
                p_data = patient_res[0][TABLE_PATIENTS]
                p_phone = p_data.get("phone", "") if patient_res else ""
                c_name = clinic_res[0]["Clinics"]["name"] if clinic_res else "CareDesk"
                d_name = doctor_res[0][TABLE_DOCTORS]["name"] if doctor_res else ""
                if p_phone:
                    send_booking_sms(p_phone, p_data.get("name", ""), d_name, token, appt_time, appt_date, c_name)
        except Exception as sms_err:
            logger.warning(f"SMS send failed (non-critical): {sms_err}")

        # Emit signal for new booking
        emit_appointment_event(app, clinic_id, "booked", {
            "appointment_id": row["ROWID"],
            "token_number": token,
        })

        return created({
            "id": row["ROWID"],
            "token_number": token,
            "status": STATUS_BOOKED,
            "appointment_date": appt_date,
            "appointment_time": appt_time,
        }, "Appointment booked successfully")

    except Exception as e:
        logger.error(f"Create appointment error: {e}")
        return server_error(str(e))


def update_status(app, request, appointment_id):
    """PUT /api/appointments/:id — Update appointment status."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        body = request.get_json(silent=True) or {}
        new_status = body.get("status", "").strip()

        if new_status not in VALID_STATUSES:
            return error(f"Invalid status. Must be one of: {VALID_STATUSES}")

        # Get current appointment
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, status FROM {TABLE_APPOINTMENTS} "
            f"WHERE ROWID = '{appointment_id}' AND clinic_id = '{clinic_id}'"
        )
        if not result or len(result) == 0:
            return not_found("Appointment not found")

        current_status = result[0][TABLE_APPOINTMENTS]["status"]

        # Validate status transition
        allowed = STATUS_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            return error(
                f"Cannot change from '{current_status}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        # Validate: doctor can only consult one patient at a time
        if new_status == "in-consultation":
            today = ist_today()
            doctor_result = zcql.execute_query(
                f"SELECT doctor_id FROM {TABLE_APPOINTMENTS} "
                f"WHERE ROWID = '{appointment_id}'"
            )
            if doctor_result:
                doc_id = doctor_result[0][TABLE_APPOINTMENTS]["doctor_id"]
                busy = zcql.execute_query(
                    f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
                    f"WHERE clinic_id = '{clinic_id}' AND doctor_id = '{doc_id}' "
                    f"AND appointment_date = '{today}' "
                    f"AND status = 'in-consultation' "
                    f"AND ROWID != '{appointment_id}'"
                )
                if busy and len(busy) > 0:
                    return error("This doctor is already consulting another patient")

        table = app.datastore().table(TABLE_APPOINTMENTS)
        row = table.update_row({
            "ROWID": appointment_id,
            "status": new_status,
        })

        # Update queue cache
        _refresh_queue_cache(app, clinic_id)

        # Emit real-time signal for queue displays
        emit_queue_update(app, clinic_id, {
            "appointment_id": appointment_id,
            "old_status": current_status,
            "new_status": new_status,
        })
        emit_appointment_event(app, clinic_id, "status_changed", {
            "appointment_id": appointment_id,
            "status": new_status,
        })

        return success({
            "id": row["ROWID"],
            "status": new_status,
        }, f"Status updated to '{new_status}'")

    except Exception as e:
        logger.error(f"Update appointment error: {e}")
        return server_error(str(e))


def by_patient(app, request, patient_id):
    """GET /api/appointments/patient/:id — All appointments for a patient."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.doctor_id, "
            f"{TABLE_APPOINTMENTS}.appointment_date, {TABLE_APPOINTMENTS}.appointment_time, "
            f"{TABLE_APPOINTMENTS}.status, {TABLE_APPOINTMENTS}.token_number, "
            f"{TABLE_APPOINTMENTS}.notes, {TABLE_APPOINTMENTS}.feedback_score, "
            f"{TABLE_APPOINTMENTS}.feedback_sentiment, {TABLE_DOCTORS}.name "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.patient_id = '{patient_id}' "
            f"ORDER BY {TABLE_APPOINTMENTS}.appointment_date DESC, "
            f"{TABLE_APPOINTMENTS}.appointment_time DESC"
        )

        appointments = []
        for row in (result or []):
            a = row[TABLE_APPOINTMENTS]
            d = row.get(TABLE_DOCTORS, {})
            appointments.append({
                "id": a["ROWID"],
                "doctor_id": a["doctor_id"],
                "doctor_name": d.get("name", ""),
                "appointment_date": a["appointment_date"],
                "appointment_time": a["appointment_time"],
                "status": a["status"],
                "token_number": a["token_number"],
                "notes": a["notes"],
                "feedback_score": a.get("feedback_score", ""),
                "feedback_sentiment": a.get("feedback_sentiment", ""),
            })

        return success(appointments)

    except Exception as e:
        logger.error(f"Patient appointments error: {e}")
        return server_error(str(e))


def get_queue(app, request):
    """GET /api/appointments/queue — Get live queue for today."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        return _build_queue_response(app, clinic_id)

    except Exception as e:
        logger.error(f"Get queue error: {e}")
        return server_error(str(e))


def _build_queue_response(app, clinic_id):
    """Build queue response from DB."""
    today = ist_today()
    zcql = app.zcql()
    result = zcql.execute_query(
        f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.token_number, "
        f"{TABLE_APPOINTMENTS}.status, {TABLE_APPOINTMENTS}.appointment_time, "
        f"{TABLE_APPOINTMENTS}.doctor_id, "
        f"{TABLE_DOCTORS}.name, {TABLE_PATIENTS}.name "
        f"FROM {TABLE_APPOINTMENTS} "
        f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
        f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_APPOINTMENTS}.patient_id = {TABLE_PATIENTS}.ROWID "
        f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
        f"AND {TABLE_APPOINTMENTS}.appointment_date = '{today}' "
        f"AND {TABLE_APPOINTMENTS}.status IN ('{STATUS_IN_QUEUE}', 'in-consultation') "
        f"ORDER BY {TABLE_APPOINTMENTS}.token_number ASC"
    )

    queue = []
    for row in (result or []):
        a = row[TABLE_APPOINTMENTS]
        queue.append({
            "id": a["ROWID"],
            "token_number": a["token_number"],
            "status": a["status"],
            "appointment_time": a["appointment_time"],
            "doctor_name": row.get(TABLE_DOCTORS, {}).get("name", ""),
            "patient_name": row.get(TABLE_PATIENTS, {}).get("name", ""),
        })

    return success(queue)


def list_feedback(app, request):
    """GET /api/appointments/feedback — All appointments with feedback."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.appointment_date, "
            f"{TABLE_APPOINTMENTS}.appointment_time, {TABLE_APPOINTMENTS}.token_number, "
            f"{TABLE_APPOINTMENTS}.feedback_score, {TABLE_APPOINTMENTS}.feedback_text, "
            f"{TABLE_APPOINTMENTS}.feedback_sentiment, {TABLE_APPOINTMENTS}.feedback_keywords, "
            f"{TABLE_APPOINTMENTS}.doctor_id, "
            f"{TABLE_DOCTORS}.name, {TABLE_PATIENTS}.name, {TABLE_PATIENTS}.phone "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_APPOINTMENTS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.feedback_score != '' "
            f"ORDER BY {TABLE_APPOINTMENTS}.appointment_date DESC, "
            f"{TABLE_APPOINTMENTS}.appointment_time DESC"
        )

        feedbacks = []
        for row in (result or []):
            a = row[TABLE_APPOINTMENTS]
            d = row.get(TABLE_DOCTORS, {})
            p = row.get(TABLE_PATIENTS, {})
            kw_str = a.get("feedback_keywords", "")
            feedbacks.append({
                "id": a["ROWID"],
                "patient_name": p.get("name", ""),
                "patient_phone": p.get("phone", ""),
                "doctor_id": a.get("doctor_id", ""),
                "doctor_name": d.get("name", ""),
                "appointment_date": a["appointment_date"],
                "appointment_time": a["appointment_time"],
                "token_number": a["token_number"],
                "feedback_score": a.get("feedback_score", ""),
                "feedback_text": a.get("feedback_text", ""),
                "feedback_sentiment": a.get("feedback_sentiment", ""),
                "feedback_keywords": [k.strip() for k in kw_str.split(",") if k.strip()] if kw_str else [],
            })

        return success(feedbacks)

    except Exception as e:
        logger.error(f"List feedback error: {e}")
        return server_error(str(e))


def _refresh_queue_cache(app, clinic_id):
    """Refresh the queue cache after status change."""
    try:
        today = ist_today()
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, token_number, status, doctor_id "
            f"FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' "
            f"AND appointment_date = '{today}' "
            f"AND status IN ('{STATUS_IN_QUEUE}', 'in-consultation') "
            f"ORDER BY token_number ASC"
        )
        queue_data = []
        for row in (result or []):
            a = row[TABLE_APPOINTMENTS]
            queue_data.append({
                "id": a["ROWID"],
                "token": a["token_number"],
                "status": a["status"],
            })
        set_queue_state(app, clinic_id, queue_data)
    except Exception as e:
        logger.warning(f"Queue cache refresh failed: {e}")
