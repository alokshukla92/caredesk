import re
import logging
from flask import Request, make_response, jsonify
import zcatalyst_sdk

from routes import clinic_routes, doctor_routes, patient_routes
from routes import appointment_routes, prescription_routes
from routes import public_routes, dashboard_routes, cron_routes
from utils.response import error, not_found

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(request: Request):
    """
    Main request router for CareDesk HMS.
    Routes incoming requests to the appropriate handler based on path and method.
    """
    app = zcatalyst_sdk.initialize(req=request)
    path = request.path
    method = request.method.upper()

    logger.info(f"{method} {path}")

    # ── Public Routes (no auth required) ────────────────────────────

    # GET /api/public/clinic/:slug
    match = re.match(r"^/api/public/clinic/([a-z0-9\-]+)$", path)
    if match and method == "GET":
        return public_routes.get_clinic(app, request, match.group(1))

    # POST /api/public/book
    if path == "/api/public/book" and method == "POST":
        return public_routes.book_appointment(app, request)

    # GET /api/public/queue/:slug
    match = re.match(r"^/api/public/queue/([a-z0-9\-]+)$", path)
    if match and method == "GET":
        return public_routes.get_queue(app, request, match.group(1))

    # POST /api/public/feedback/:appointment_id
    match = re.match(r"^/api/public/feedback/(\d+)$", path)
    if match and method == "POST":
        return public_routes.submit_feedback(app, request, match.group(1))

    # ── Clinic Routes ───────────────────────────────────────────────

    if path == "/api/clinics" and method == "POST":
        return clinic_routes.create(app, request)

    if path == "/api/clinics/me" and method == "GET":
        return clinic_routes.get_mine(app, request)

    if path == "/api/clinics/me" and method == "PUT":
        return clinic_routes.update_mine(app, request)

    # ── Doctor Routes ───────────────────────────────────────────────

    if path == "/api/doctors" and method == "GET":
        return doctor_routes.list_all(app, request)

    if path == "/api/doctors" and method == "POST":
        return doctor_routes.create(app, request)

    match = re.match(r"^/api/doctors/(\d+)$", path)
    if match and method == "PUT":
        return doctor_routes.update(app, request, match.group(1))

    if match and method == "DELETE":
        return doctor_routes.delete(app, request, match.group(1))

    # ── Patient Routes ──────────────────────────────────────────────

    if path == "/api/patients/search" and method == "GET":
        return patient_routes.search(app, request)

    if path == "/api/patients" and method == "GET":
        return patient_routes.list_all(app, request)

    if path == "/api/patients" and method == "POST":
        return patient_routes.create(app, request)

    match = re.match(r"^/api/patients/(\d+)$", path)
    if match and method == "GET":
        return patient_routes.get_one(app, request, match.group(1))

    if match and method == "PUT":
        return patient_routes.update(app, request, match.group(1))

    # ── Appointment Routes ──────────────────────────────────────────

    if path == "/api/appointments/queue" and method == "GET":
        return appointment_routes.get_queue(app, request)

    if path == "/api/appointments" and method == "GET":
        return appointment_routes.list_today(app, request)

    if path == "/api/appointments" and method == "POST":
        return appointment_routes.create(app, request)

    match = re.match(r"^/api/appointments/(\d+)$", path)
    if match and method == "PUT":
        return appointment_routes.update_status(app, request, match.group(1))

    # ── Prescription Routes ─────────────────────────────────────────

    if path == "/api/prescriptions" and method == "POST":
        return prescription_routes.create(app, request)

    match = re.match(r"^/api/prescriptions/patient/(\d+)$", path)
    if match and method == "GET":
        return prescription_routes.by_patient(app, request, match.group(1))

    match = re.match(r"^/api/prescriptions/(\d+)$", path)
    if match and method == "GET":
        return prescription_routes.get_one(app, request, match.group(1))

    # ── Clinic Logo Upload ─────────────────────────────────────────

    if path == "/api/clinics/me/logo" and method == "POST":
        return clinic_routes.upload_logo(app, request)

    # ── Dashboard Routes ────────────────────────────────────────────

    if path == "/api/dashboard/stats" and method == "GET":
        return dashboard_routes.get_stats(app, request)

    # ── Cron / Job Scheduling Routes ───────────────────────────────

    if path == "/api/cron/follow-up-reminders" and method == "GET":
        return cron_routes.send_follow_up_reminders(app, request)

    if path == "/api/cron/daily-digest" and method == "GET":
        return cron_routes.generate_daily_digest(app, request)

    # ── Verify Tables ───────────────────────────────────────────────

    if path == "/api/verify-tables" and method == "GET":
        return _verify_tables(app)

    # ── Debug: Who Am I ───────────────────────────────────────────

    if path == "/api/debug/whoami" and method == "GET":
        try:
            trace = []

            # 0. Dump ALL SDK-relevant headers from request
            sdk_headers = {}
            for h in ["X-ZC-ProjectId", "X-ZC-Project-Domain", "X-ZC-Project-Key",
                       "X-ZC-Environment", "X-ZC-Admin-Cred-Type", "X-ZC-User-Cred-Type",
                       "X-ZC-Admin-Cred-Token", "X-ZC-User-Cred-Token", "x-zc-cookie",
                       "X-ZC-User-Type", "Authorization", "Cookie"]:
                val = request.headers.get(h, "")
                if val:
                    # Truncate sensitive values
                    if "token" in h.lower() or "cookie" in h.lower() or h == "Authorization" or h == "Cookie":
                        sdk_headers[h] = val[:60] + "..." if len(val) > 60 else val
                    else:
                        sdk_headers[h] = val

            # 1. Raw SDK get_current_user
            raw_user = None
            try:
                auth_svc = app.authentication()
                raw_user = auth_svc.get_current_user()
                trace.append(f"get_current_user() OK: user_id={raw_user.get('user_id')}, email={raw_user.get('email_id')}")
            except Exception as auth_err:
                trace.append(f"get_current_user() FAILED: {auth_err}")

            user_id = str(raw_user.get("user_id", "")) if raw_user else None

            # 2. Direct ZCQL lookup
            zcql = app.zcql()
            if user_id:
                trace.append(f"ZCQL: WHERE admin_user_id = '{user_id}'")
                lookup = zcql.execute_query(
                    f"SELECT ROWID, name, admin_user_id FROM Clinics "
                    f"WHERE admin_user_id = '{user_id}'"
                )
                if lookup and len(lookup) > 0:
                    trace.append(f"MATCH: {lookup[0]['Clinics']}")
                else:
                    trace.append("NO MATCH — this user has no clinic")

            # 3. All clinics
            clinics = zcql.execute_query(
                "SELECT ROWID, name, slug, admin_user_id FROM Clinics"
            )
            clinic_list = []
            for row in (clinics or []):
                c = row["Clinics"]
                clinic_list.append({
                    "id": c["ROWID"],
                    "name": c["name"],
                    "admin_user_id": c["admin_user_id"],
                    "match": c["admin_user_id"] == user_id,
                })

            return make_response(jsonify({
                "user_id": user_id,
                "email": raw_user.get("email_id") if raw_user else None,
                "sdk_headers": sdk_headers,
                "trace": trace,
                "clinics_in_db": clinic_list,
            }), 200)
        except Exception as e:
            import traceback
            return make_response(jsonify({
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
            }), 200)

    # ── Health Check ────────────────────────────────────────────────

    if path == "/" and method == "GET":
        return make_response(jsonify({
            "status": "success",
            "message": "CareDesk HMS API is running",
            "version": "1.0.0",
        }), 200)

    # ── 404 Fallback ────────────────────────────────────────────────

    return not_found(f"Route not found: {method} {path}")


def _verify_tables(app):
    """GET /api/verify-tables — Check all tables exist with correct columns."""
    zcql = app.zcql()
    results = {}

    expected = {
        "Clinics": {
            "columns": ["name", "slug", "address", "phone", "email", "admin_user_id", "logo_url"],
            "fk_count": 0,
        },
        "Doctors": {
            "columns": ["clinic_id", "name", "specialty", "email", "phone", "available_from", "available_to", "consultation_fee", "status"],
            "fk_count": 1,
        },
        "Patients": {
            "columns": ["clinic_id", "name", "phone", "email", "age", "gender", "blood_group", "medical_history"],
            "fk_count": 1,
        },
        "Appointments": {
            "columns": ["clinic_id", "doctor_id", "patient_id", "appointment_date", "appointment_time", "status", "token_number", "notes", "feedback_score", "feedback_text", "feedback_sentiment"],
            "fk_count": 3,
        },
        "Prescriptions": {
            "columns": ["clinic_id", "appointment_id", "doctor_id", "patient_id", "diagnosis", "medicines", "advice", "follow_up_date", "prescription_url"],
            "fk_count": 4,
        },
    }

    all_ok = True
    for table_name, spec in expected.items():
        table_result = {"exists": False, "columns_found": [], "columns_missing": [], "status": "FAIL"}
        try:
            # Try a simple SELECT to check if table exists
            query = f"SELECT * FROM {table_name} LIMIT 1"
            zcql.execute_query(query)
            table_result["exists"] = True

            # Check columns by trying to select each one
            found = []
            missing = []
            for col in spec["columns"]:
                try:
                    zcql.execute_query(f"SELECT {col} FROM {table_name} LIMIT 1")
                    found.append(col)
                except Exception:
                    missing.append(col)

            table_result["columns_found"] = found
            table_result["columns_missing"] = missing
            table_result["expected_columns"] = len(spec["columns"])
            table_result["found_columns"] = len(found)
            table_result["expected_fk_count"] = spec["fk_count"]

            if len(missing) == 0:
                table_result["status"] = "OK"
            else:
                table_result["status"] = "PARTIAL"
                all_ok = False

        except Exception as e:
            table_result["error"] = str(e)
            all_ok = False

        results[table_name] = table_result

    status_code = 200 if all_ok else 207
    return make_response(jsonify({
        "status": "success" if all_ok else "partial",
        "message": "All tables verified!" if all_ok else "Some tables have issues",
        "tables": results,
    }), status_code)
