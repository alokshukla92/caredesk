import json
import logging
from utils.constants import (
    TABLE_PRESCRIPTIONS, TABLE_APPOINTMENTS, TABLE_DOCTORS, TABLE_PATIENTS,
    TABLE_CLINICS, STATUS_COMPLETED, ist_today,
)
from utils.response import success, created, error, not_found, server_error
from services.auth_service import require_clinic
from services.mail_service import send_prescription_email
from services.smart_browz_service import generate_prescription_html, generate_pdf
from services.stratus_service import upload_prescription_pdf, get_file_download_url
from services.sms_service import send_prescription_sms

logger = logging.getLogger(__name__)


def create(app, request):
    """POST /api/prescriptions — Create a new prescription."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        body = request.get_json(silent=True) or {}
        appointment_id = body.get("appointment_id", "").strip()
        diagnosis = body.get("diagnosis", "").strip()
        medicines = body.get("medicines", [])
        advice = body.get("advice", "")
        follow_up_date = body.get("follow_up_date", "")

        if not appointment_id or not diagnosis:
            return error("Appointment ID and diagnosis are required")

        # Get appointment details
        zcql = app.zcql()
        appt_result = zcql.execute_query(
            f"SELECT ROWID, doctor_id, patient_id FROM {TABLE_APPOINTMENTS} "
            f"WHERE ROWID = '{appointment_id}' AND clinic_id = '{clinic_id}'"
        )
        if not appt_result or len(appt_result) == 0:
            return not_found("Appointment not found")

        appt = appt_result[0][TABLE_APPOINTMENTS]
        doctor_id = appt["doctor_id"]
        patient_id = appt["patient_id"]

        # Store medicines as JSON string
        medicines_json = json.dumps(medicines) if isinstance(medicines, list) else str(medicines)

        table = app.datastore().table(TABLE_PRESCRIPTIONS)
        row = table.insert_row({
            "clinic_id": clinic_id,
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "medicines": medicines_json,
            "advice": advice,
            "follow_up_date": follow_up_date,
            "prescription_url": "",
        })

        # Update appointment status to completed
        try:
            appt_table = app.datastore().table(TABLE_APPOINTMENTS)
            appt_table.update_row({
                "ROWID": appointment_id,
                "status": STATUS_COMPLETED,
            })
        except Exception as status_err:
            logger.warning(f"Failed to update appointment status: {status_err}")

        # Fetch clinic, doctor, patient details for email + PDF
        clinic_res = zcql.execute_query(
            f"SELECT name, address, phone FROM {TABLE_CLINICS} WHERE ROWID = '{clinic_id}'"
        )
        doctor_res = zcql.execute_query(
            f"SELECT name, specialty FROM {TABLE_DOCTORS} WHERE ROWID = '{doctor_id}'"
        )
        patient_res = zcql.execute_query(
            f"SELECT name, email, phone, age, gender FROM {TABLE_PATIENTS} WHERE ROWID = '{patient_id}'"
        )

        clinic_data = clinic_res[0][TABLE_CLINICS] if clinic_res else {}
        doctor_data = doctor_res[0][TABLE_DOCTORS] if doctor_res else {}
        patient_data = patient_res[0][TABLE_PATIENTS] if patient_res else {}

        # Send prescription email (non-blocking)
        try:
            p_email = patient_data.get("email", "")
            if p_email:
                medicines_text = "<br>".join(
                    [f"- {m.get('name', '')} | {m.get('dosage', '')} | {m.get('duration', '')} | {m.get('instructions', '')}"
                     for m in medicines]
                ) if isinstance(medicines, list) else str(medicines)

                send_prescription_email(
                    app,
                    patient_email=p_email,
                    patient_name=patient_data.get("name", ""),
                    doctor_name=doctor_data.get("name", ""),
                    clinic_name=clinic_data.get("name", "CareDesk"),
                    diagnosis=diagnosis,
                    medicines_text=medicines_text,
                    advice=advice,
                )
        except Exception as mail_err:
            logger.warning(f"Prescription mail failed: {mail_err}")

        # Send prescription SMS
        try:
            p_phone = patient_data.get("phone", "")
            if p_phone:
                send_prescription_sms(
                    p_phone,
                    patient_data.get("name", ""),
                    doctor_data.get("name", ""),
                    diagnosis,
                    medicines if isinstance(medicines, list) else [],
                    advice,
                    follow_up_date,
                )
        except Exception as sms_err:
            logger.warning(f"Prescription SMS failed (non-critical): {sms_err}")

        # Generate prescription PDF via SmartBrowz + store in Stratus
        prescription_url = ""
        try:
            html_content = generate_prescription_html({
                "clinic_name": clinic_data.get("name", "CareDesk"),
                "clinic_address": clinic_data.get("address", ""),
                "clinic_phone": clinic_data.get("phone", ""),
                "doctor_name": doctor_data.get("name", ""),
                "doctor_specialty": doctor_data.get("specialty", ""),
                "patient_name": patient_data.get("name", ""),
                "patient_age": patient_data.get("age", ""),
                "patient_gender": patient_data.get("gender", ""),
                "diagnosis": diagnosis,
                "medicines": medicines if isinstance(medicines, list) else [],
                "advice": advice,
                "follow_up_date": follow_up_date,
                "date": ist_today(),
                "prescription_id": row["ROWID"],
            })
            pdf_bytes = generate_pdf(app, html_content)
            if pdf_bytes:
                file_id = upload_prescription_pdf(app, pdf_bytes, row["ROWID"])
                if file_id:
                    prescription_url = str(file_id)
                    table.update_row({"ROWID": row["ROWID"], "prescription_url": prescription_url})
                    logger.info(f"Prescription PDF stored: {prescription_url}")
        except Exception as pdf_err:
            logger.warning(f"PDF generation failed (non-critical): {pdf_err}")

        return created({
            "id": row["ROWID"],
            "appointment_id": appointment_id,
            "diagnosis": diagnosis,
            "medicines": medicines,
            "advice": advice,
            "follow_up_date": follow_up_date,
            "prescription_url": prescription_url,
        }, "Prescription created successfully")

    except Exception as e:
        logger.error(f"Create prescription error: {e}")
        return server_error(str(e))


def get_one(app, request, prescription_id):
    """GET /api/prescriptions/:id — Get a prescription."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.appointment_id, "
            f"{TABLE_PRESCRIPTIONS}.diagnosis, {TABLE_PRESCRIPTIONS}.medicines, "
            f"{TABLE_PRESCRIPTIONS}.advice, {TABLE_PRESCRIPTIONS}.follow_up_date, "
            f"{TABLE_PRESCRIPTIONS}.prescription_url, {TABLE_PRESCRIPTIONS}.CREATEDTIME, "
            f"{TABLE_DOCTORS}.name, {TABLE_DOCTORS}.specialty, "
            f"{TABLE_PATIENTS}.name, {TABLE_PATIENTS}.age, {TABLE_PATIENTS}.gender "
            f"FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_PRESCRIPTIONS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_PRESCRIPTIONS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.ROWID = '{prescription_id}' "
            f"AND {TABLE_PRESCRIPTIONS}.clinic_id = '{clinic_id}'"
        )

        if not result or len(result) == 0:
            return not_found("Prescription not found")

        rx = result[0][TABLE_PRESCRIPTIONS]
        d = result[0].get(TABLE_DOCTORS, {})
        p = result[0].get(TABLE_PATIENTS, {})

        # Get clinic info
        clinic_res = zcql.execute_query(
            f"SELECT name, address, phone FROM {TABLE_CLINICS} WHERE ROWID = '{clinic_id}'"
        )
        clinic_data = clinic_res[0][TABLE_CLINICS] if clinic_res else {}

        medicines = rx["medicines"]
        try:
            medicines = json.loads(medicines)
        except (json.JSONDecodeError, TypeError):
            pass

        return success({
            "id": rx["ROWID"],
            "appointment_id": rx["appointment_id"],
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
            "prescription_url": rx["prescription_url"],
            "created_time": rx["CREATEDTIME"],
        })

    except Exception as e:
        logger.error(f"Get prescription error: {e}")
        return server_error(str(e))


def download_pdf(app, request, prescription_id):
    """GET /api/prescriptions/:id/pdf — Download or regenerate prescription PDF."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.prescription_url, "
            f"{TABLE_PRESCRIPTIONS}.diagnosis, {TABLE_PRESCRIPTIONS}.medicines, "
            f"{TABLE_PRESCRIPTIONS}.advice, {TABLE_PRESCRIPTIONS}.follow_up_date, "
            f"{TABLE_PRESCRIPTIONS}.doctor_id, {TABLE_PRESCRIPTIONS}.patient_id, "
            f"{TABLE_DOCTORS}.name, {TABLE_DOCTORS}.specialty, "
            f"{TABLE_PATIENTS}.name, {TABLE_PATIENTS}.age, {TABLE_PATIENTS}.gender "
            f"FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_PRESCRIPTIONS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_PRESCRIPTIONS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.ROWID = '{prescription_id}' "
            f"AND {TABLE_PRESCRIPTIONS}.clinic_id = '{clinic_id}'"
        )

        if not result or len(result) == 0:
            return not_found("Prescription not found")

        rx = result[0][TABLE_PRESCRIPTIONS]
        d = result[0].get(TABLE_DOCTORS, {})
        p = result[0].get(TABLE_PATIENTS, {})

        # If PDF already exists in Stratus, return its download URL
        existing_url = rx.get("prescription_url", "")
        if existing_url:
            download_url = get_file_download_url(app, existing_url)
            if download_url:
                return success({
                    "download_url": download_url,
                    "source": "stratus",
                })

        # Otherwise, regenerate the PDF
        clinic_res = zcql.execute_query(
            f"SELECT name, address, phone FROM {TABLE_CLINICS} WHERE ROWID = '{clinic_id}'"
        )
        clinic_data = clinic_res[0][TABLE_CLINICS] if clinic_res else {}

        medicines = rx["medicines"]
        try:
            medicines = json.loads(medicines)
        except (json.JSONDecodeError, TypeError):
            medicines = []

        html_content = generate_prescription_html({
            "clinic_name": clinic_data.get("name", "CareDesk"),
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
            "date": rx.get("CREATEDTIME", ist_today()).split("T")[0] if "T" in rx.get("CREATEDTIME", "") else ist_today(),
            "prescription_id": prescription_id,
        })

        pdf_bytes = generate_pdf(app, html_content)
        if not pdf_bytes:
            return error("PDF generation failed. Please try printing from the view page.")

        # Upload to Stratus
        file_id = upload_prescription_pdf(app, pdf_bytes, prescription_id)
        if file_id:
            # Save URL for future downloads
            table = app.datastore().table(TABLE_PRESCRIPTIONS)
            table.update_row({"ROWID": prescription_id, "prescription_url": str(file_id)})

            download_url = get_file_download_url(app, str(file_id))
            if download_url:
                return success({
                    "download_url": download_url,
                    "source": "regenerated",
                })

        return error("Failed to generate and store PDF")

    except Exception as e:
        logger.error(f"Download PDF error: {e}")
        return server_error(str(e))


def by_patient(app, request, patient_id):
    """GET /api/prescriptions/patient/:id — Patient's prescription history."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.diagnosis, "
            f"{TABLE_PRESCRIPTIONS}.medicines, {TABLE_PRESCRIPTIONS}.advice, "
            f"{TABLE_PRESCRIPTIONS}.follow_up_date, {TABLE_PRESCRIPTIONS}.CREATEDTIME, "
            f"{TABLE_DOCTORS}.name "
            f"FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_PRESCRIPTIONS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.patient_id = '{patient_id}' "
            f"AND {TABLE_PRESCRIPTIONS}.clinic_id = '{clinic_id}' "
            f"ORDER BY {TABLE_PRESCRIPTIONS}.ROWID DESC"
        )

        prescriptions = []
        for row in (result or []):
            rx = row[TABLE_PRESCRIPTIONS]
            medicines = rx["medicines"]
            try:
                medicines = json.loads(medicines)
            except (json.JSONDecodeError, TypeError):
                pass

            prescriptions.append({
                "id": rx["ROWID"],
                "doctor_name": row.get(TABLE_DOCTORS, {}).get("name", ""),
                "diagnosis": rx["diagnosis"],
                "medicines": medicines,
                "advice": rx["advice"],
                "follow_up_date": rx["follow_up_date"],
                "created_time": rx["CREATEDTIME"],
            })

        return success(prescriptions)

    except Exception as e:
        logger.error(f"Get patient prescriptions error: {e}")
        return server_error(str(e))
