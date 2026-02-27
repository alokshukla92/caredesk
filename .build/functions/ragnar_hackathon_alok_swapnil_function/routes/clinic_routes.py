import json
import logging
from utils.constants import TABLE_CLINICS
from utils.response import success, created, error, not_found, server_error
from services.auth_service import get_current_user, get_clinic_id
from services.stratus_service import upload_clinic_logo

logger = logging.getLogger(__name__)


def create(app, request):
    """POST /api/clinics — Register a new clinic (creates tenant)."""
    try:
        user = get_current_user(app)
        if not user:
            user = {"user_id": "dev"}

        body = request.get_json(silent=True) or {}
        name = body.get("name", "").strip()
        slug = body.get("slug", "").strip().lower().replace(" ", "-")

        if not name or not slug:
            return error("Clinic name and slug are required")

        user_id = str(user.get("user_id", ""))

        # Check if user already has a clinic
        zcql = app.zcql()
        existing = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_CLINICS} WHERE admin_user_id = '{user_id}'"
        )
        if existing and len(existing) > 0:
            return error("You already have a registered clinic")

        # Check if slug is taken
        slug_check = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_CLINICS} WHERE slug = '{slug}'"
        )
        if slug_check and len(slug_check) > 0:
            return error("This slug is already taken")

        # Create clinic
        table = app.datastore().table(TABLE_CLINICS)
        row = table.insert_row({
            "name": name,
            "slug": slug,
            "address": body.get("address", ""),
            "phone": body.get("phone", ""),
            "email": body.get("email", ""),
            "admin_user_id": user_id,
            "logo_url": "",
        })

        return created({
            "id": row["ROWID"],
            "name": row["name"],
            "slug": row["slug"],
            "address": row["address"],
            "phone": row["phone"],
            "email": row["email"],
        }, "Clinic registered successfully")

    except Exception as e:
        logger.error(f"Create clinic error: {e}")
        return server_error(str(e))


def get_mine(app, request):
    """GET /api/clinics/me — Get current user's clinic."""
    try:
        clinic_id, user = get_clinic_id(app, request)
        user_id = str(user.get("user_id", "")) if user else None
        logger.info(f"get_mine: user_id={user_id}, clinic_id={clinic_id}")

        if not clinic_id:
            return not_found(f"No clinic found. Please register first. (user_id={user_id})")

        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID, name, slug, address, phone, email, logo_url, CREATEDTIME "
            f"FROM {TABLE_CLINICS} WHERE ROWID = '{clinic_id}'"
        )

        if not result or len(result) == 0:
            return not_found("Clinic not found")

        clinic = result[0][TABLE_CLINICS]
        return success({
            "id": clinic["ROWID"],
            "name": clinic["name"],
            "slug": clinic["slug"],
            "address": clinic["address"],
            "phone": clinic["phone"],
            "email": clinic["email"],
            "logo_url": clinic["logo_url"],
            "created_time": clinic["CREATEDTIME"],
            "_debug_user_id": user_id,
        })

    except Exception as e:
        logger.error(f"Get clinic error: {e}")
        return server_error(str(e))


def update_mine(app, request):
    """PUT /api/clinics/me — Update current user's clinic."""
    try:
        clinic_id, user = get_clinic_id(app, request)
        if not clinic_id:
            return not_found("No clinic found")

        body = request.get_json(silent=True) or {}
        update_data = {"ROWID": clinic_id}

        for field in ["name", "address", "phone", "email", "logo_url"]:
            if field in body:
                update_data[field] = body[field]

        table = app.datastore().table(TABLE_CLINICS)
        row = table.update_row(update_data)

        return success({
            "id": row["ROWID"],
            "name": row.get("name", ""),
            "slug": row.get("slug", ""),
            "address": row.get("address", ""),
            "phone": row.get("phone", ""),
            "email": row.get("email", ""),
        }, "Clinic updated successfully")

    except Exception as e:
        logger.error(f"Update clinic error: {e}")
        return server_error(str(e))


def upload_logo(app, request):
    """POST /api/clinics/me/logo — Upload clinic logo to Stratus."""
    try:
        clinic_id, user = get_clinic_id(app, request)
        if not clinic_id:
            return not_found("No clinic found")

        file = request.files.get("logo")
        if not file:
            return error("Logo file is required")

        file_content = file.read()
        file_name = file.filename or "logo.png"

        file_id = upload_clinic_logo(app, file_content, clinic_id, file_name)
        if not file_id:
            return error("Failed to upload logo")

        # Update clinic record with logo file ID
        table = app.datastore().table(TABLE_CLINICS)
        table.update_row({"ROWID": clinic_id, "logo_url": str(file_id)})

        return success({"logo_url": str(file_id)}, "Logo uploaded successfully")

    except Exception as e:
        logger.error(f"Logo upload error: {e}")
        return server_error(str(e))
