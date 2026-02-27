import logging
from utils.constants import TABLE_DOCTORS
from utils.response import success, created, error, not_found, server_error
from services.auth_service import require_clinic

logger = logging.getLogger(__name__)


def list_all(app, request):
    """GET /api/doctors — List all doctors for the clinic."""
    try:
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found. Register first.", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, specialty, email, phone, available_from, "
            f"available_to, consultation_fee, status "
            f"FROM {TABLE_DOCTORS} WHERE clinic_id = '{clinic_id}' ORDER BY name ASC"
        )

        doctors = []
        for row in (result or []):
            d = row[TABLE_DOCTORS]
            doctors.append({
                "id": d["ROWID"],
                "name": d["name"],
                "specialty": d["specialty"],
                "email": d["email"],
                "phone": d["phone"],
                "available_from": d["available_from"],
                "available_to": d["available_to"],
                "consultation_fee": d["consultation_fee"],
                "status": d["status"],
            })

        return success(doctors)

    except Exception as e:
        logger.error(f"List doctors error: {e}")
        return server_error(str(e))


def create(app, request):
    """POST /api/doctors — Add a new doctor."""
    try:
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found", 403)

        body = request.get_json(silent=True) or {}
        name = body.get("name", "").strip()
        specialty = body.get("specialty", "").strip()

        if not name or not specialty:
            return error("Doctor name and specialty are required")

        table = app.datastore().table(TABLE_DOCTORS)
        row = table.insert_row({
            "clinic_id": clinic_id,
            "name": name,
            "specialty": specialty,
            "email": body.get("email", ""),
            "phone": body.get("phone", ""),
            "available_from": body.get("available_from", "09:00"),
            "available_to": body.get("available_to", "17:00"),
            "consultation_fee": body.get("consultation_fee", "500"),
            "status": "active",
        })

        return created({
            "id": row["ROWID"],
            "name": row["name"],
            "specialty": row["specialty"],
            "email": row["email"],
            "phone": row["phone"],
            "available_from": row["available_from"],
            "available_to": row["available_to"],
            "consultation_fee": row["consultation_fee"],
            "status": row["status"],
        }, "Doctor added successfully")

    except Exception as e:
        logger.error(f"Create doctor error: {e}")
        return server_error(str(e))


def update(app, request, doctor_id):
    """PUT /api/doctors/:id — Update a doctor."""
    try:
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found", 403)

        # Verify doctor belongs to this clinic
        zcql = app.zcql()
        check = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_DOCTORS} "
            f"WHERE ROWID = '{doctor_id}' AND clinic_id = '{clinic_id}'"
        )
        if not check or len(check) == 0:
            return not_found("Doctor not found")

        body = request.get_json(silent=True) or {}
        update_data = {"ROWID": doctor_id}

        for field in ["name", "specialty", "email", "phone",
                      "available_from", "available_to", "consultation_fee", "status"]:
            if field in body:
                update_data[field] = body[field]

        table = app.datastore().table(TABLE_DOCTORS)
        row = table.update_row(update_data)

        return success({
            "id": row["ROWID"],
            "name": row.get("name", ""),
            "specialty": row.get("specialty", ""),
            "status": row.get("status", ""),
        }, "Doctor updated")

    except Exception as e:
        logger.error(f"Update doctor error: {e}")
        return server_error(str(e))


def delete(app, request, doctor_id):
    """DELETE /api/doctors/:id — Remove a doctor."""
    try:
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found", 403)

        # Verify doctor belongs to this clinic
        zcql = app.zcql()
        check = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_DOCTORS} "
            f"WHERE ROWID = '{doctor_id}' AND clinic_id = '{clinic_id}'"
        )
        if not check or len(check) == 0:
            return not_found("Doctor not found")

        table = app.datastore().table(TABLE_DOCTORS)
        table.delete_row(doctor_id)

        return success(message="Doctor removed successfully")

    except Exception as e:
        logger.error(f"Delete doctor error: {e}")
        return server_error(str(e))
