import json
import logging
from utils.constants import (
    TABLE_PRESCRIPTIONS, TABLE_APPOINTMENTS, TABLE_DOCTORS, TABLE_PATIENTS,
    STATUS_COMPLETED,
)
from utils.response import success, created, error, not_found, server_error
from services.auth_service import require_clinic
from services.mail_service import send_prescription_email
from services.smart_browz_service import generate_prescription_html, generate_pdf
from services.stratus_service import upload_prescription_pdf

logger = logging.getLogger(__name__)


def create(app, request):
    """POST /api/prescriptions — Create a new prescription."""
    try:
        clinic_id, user = require_clinic(app)
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

        # Send prescription email (non-blocking)
        try:
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
                    medicines_text = "<br>".join(
                        [f"- {m.get('name', '')} | {m.get('dosage', '')} | {m.get('duration', '')} | {m.get('instructions', '')}"
                         for m in medicines]
                    ) if isinstance(medicines, list) else str(medicines)

                    send_prescription_email(
                        app,
                        patient_email=p_email,
                        patient_name=patient_res[0][TABLE_PATIENTS]["name"],
                        doctor_name=doctor_res[0][TABLE_DOCTORS]["name"],
                        clinic_name=clinic_res[0]["Clinics"]["name"],
                        diagnosis=diagnosis,
                        medicines_text=medicines_text,
                        advice=advice,
                    )
        except Exception as mail_err:
            logger.warning(f"Prescription mail failed: {mail_err}")

        # Generate prescription PDF via SmartBrowz + store in Stratus
        prescription_url = ""
        try:
            clinic_res2 = zcql.execute_query(
                f"SELECT name FROM Clinics WHERE ROWID = '{clinic_id}'"
            )
            doctor_res2 = zcql.execute_query(
                f"SELECT name FROM {TABLE_DOCTORS} WHERE ROWID = '{doctor_id}'"
            )
            patient_res2 = zcql.execute_query(
                f"SELECT name, age, gender FROM {TABLE_PATIENTS} WHERE ROWID = '{patient_id}'"
            )
            from datetime import date as date_mod
            html_content = generate_prescription_html({
                "clinic_name": clinic_res2[0]["Clinics"]["name"] if clinic_res2 else "CareDesk",
                "doctor_name": doctor_res2[0][TABLE_DOCTORS]["name"] if doctor_res2 else "",
                "patient_name": patient_res2[0][TABLE_PATIENTS]["name"] if patient_res2 else "",
                "patient_age": patient_res2[0][TABLE_PATIENTS].get("age", "") if patient_res2 else "",
                "patient_gender": patient_res2[0][TABLE_PATIENTS].get("gender", "") if patient_res2 else "",
                "diagnosis": diagnosis,
                "medicines": medicines if isinstance(medicines, list) else [],
                "advice": advice,
                "follow_up_date": follow_up_date,
                "date": date_mod.today().isoformat(),
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
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.appointment_id, "
            f"{TABLE_PRESCRIPTIONS}.diagnosis, {TABLE_PRESCRIPTIONS}.medicines, "
            f"{TABLE_PRESCRIPTIONS}.advice, {TABLE_PRESCRIPTIONS}.follow_up_date, "
            f"{TABLE_PRESCRIPTIONS}.prescription_url, {TABLE_PRESCRIPTIONS}.CREATEDTIME, "
            f"{TABLE_DOCTORS}.name, {TABLE_PATIENTS}.name, {TABLE_PATIENTS}.age, "
            f"{TABLE_PATIENTS}.gender "
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

        medicines = rx["medicines"]
        try:
            medicines = json.loads(medicines)
        except (json.JSONDecodeError, TypeError):
            pass

        return success({
            "id": rx["ROWID"],
            "appointment_id": rx["appointment_id"],
            "doctor_name": d.get("name", ""),
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


def by_patient(app, request, patient_id):
    """GET /api/prescriptions/patient/:id — Patient's prescription history."""
    try:
        clinic_id, user = require_clinic(app)
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
