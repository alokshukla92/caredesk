import logging
from utils.constants import TABLE_PATIENTS
from utils.response import success, created, error, not_found, server_error
from services.auth_service import require_clinic
from services.search_service import search_patients

logger = logging.getLogger(__name__)


def list_all(app, request):
    """GET /api/patients — List all patients for the clinic."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, phone, email, age, gender, blood_group, medical_history "
            f"FROM {TABLE_PATIENTS} WHERE clinic_id = '{clinic_id}' ORDER BY ROWID DESC"
        )

        patients = []
        for row in (result or []):
            p = row[TABLE_PATIENTS]
            patients.append({
                "id": p["ROWID"],
                "name": p["name"],
                "phone": p["phone"],
                "email": p["email"],
                "age": p["age"],
                "gender": p["gender"],
                "blood_group": p["blood_group"],
                "medical_history": p["medical_history"],
            })

        return success(patients)

    except Exception as e:
        logger.error(f"List patients error: {e}")
        return server_error(str(e))


def create(app, request):
    """POST /api/patients — Register a new patient."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        body = request.get_json(silent=True) or {}
        name = body.get("name", "").strip()
        phone = body.get("phone", "").strip()

        if not name or not phone:
            return error("Patient name and phone are required")

        # Check for duplicate phone in same clinic
        zcql = app.zcql()
        existing = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND phone = '{phone}'"
        )
        if existing and len(existing) > 0:
            return error("Patient with this phone already exists in your clinic")

        table = app.datastore().table(TABLE_PATIENTS)
        row = table.insert_row({
            "clinic_id": clinic_id,
            "name": name,
            "phone": phone,
            "email": body.get("email", ""),
            "age": body.get("age", ""),
            "gender": body.get("gender", ""),
            "blood_group": body.get("blood_group", ""),
            "medical_history": body.get("medical_history", ""),
        })

        return created({
            "id": row["ROWID"],
            "name": row["name"],
            "phone": row["phone"],
            "email": row["email"],
            "age": row["age"],
            "gender": row["gender"],
        }, "Patient registered successfully")

    except Exception as e:
        logger.error(f"Create patient error: {e}")
        return server_error(str(e))


def get_one(app, request, patient_id):
    """GET /api/patients/:id — Get patient details."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, phone, email, age, gender, blood_group, medical_history "
            f"FROM {TABLE_PATIENTS} "
            f"WHERE ROWID = '{patient_id}' AND clinic_id = '{clinic_id}'"
        )

        if not result or len(result) == 0:
            return not_found("Patient not found")

        p = result[0][TABLE_PATIENTS]
        return success({
            "id": p["ROWID"],
            "name": p["name"],
            "phone": p["phone"],
            "email": p["email"],
            "age": p["age"],
            "gender": p["gender"],
            "blood_group": p["blood_group"],
            "medical_history": p["medical_history"],
        })

    except Exception as e:
        logger.error(f"Get patient error: {e}")
        return server_error(str(e))


def update(app, request, patient_id):
    """PUT /api/patients/:id — Update patient."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        # Verify patient belongs to this clinic
        zcql = app.zcql()
        check = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} "
            f"WHERE ROWID = '{patient_id}' AND clinic_id = '{clinic_id}'"
        )
        if not check or len(check) == 0:
            return not_found("Patient not found")

        body = request.get_json(silent=True) or {}
        update_data = {"ROWID": patient_id}

        for field in ["name", "phone", "email", "age", "gender",
                      "blood_group", "medical_history"]:
            if field in body:
                update_data[field] = body[field]

        table = app.datastore().table(TABLE_PATIENTS)
        row = table.update_row(update_data)

        return success({
            "id": row["ROWID"],
            "name": row.get("name", ""),
            "phone": row.get("phone", ""),
        }, "Patient updated")

    except Exception as e:
        logger.error(f"Update patient error: {e}")
        return server_error(str(e))


def search(app, request):
    """GET /api/patients/search?q= — Search patients by name or phone."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        query_param = request.args.get("q", "").strip()
        if not query_param:
            return error("Search query 'q' is required")

        # Try Catalyst Search service first
        search_results = search_patients(app, clinic_id, query_param)
        if search_results is not None:
            return success(search_results)

        # Fallback to ZCQL LIKE query
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, phone, email, age, gender "
            f"FROM {TABLE_PATIENTS} "
            f"WHERE clinic_id = '{clinic_id}' "
            f"AND (name LIKE '%{query_param}%' OR phone LIKE '%{query_param}%') "
            f"ORDER BY name ASC"
        )

        patients = []
        for row in (result or []):
            p = row[TABLE_PATIENTS]
            patients.append({
                "id": p["ROWID"],
                "name": p["name"],
                "phone": p["phone"],
                "email": p["email"],
                "age": p["age"],
                "gender": p["gender"],
            })

        return success(patients)

    except Exception as e:
        logger.error(f"Search patients error: {e}")
        return server_error(str(e))
