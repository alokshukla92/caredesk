import os
import logging
from utils.constants import TABLE_CLINICS

logger = logging.getLogger(__name__)


def _is_local_dev(request):
    """Check if the request is from local development (catalyst serve)."""
    if request is None:
        return False
    host = request.headers.get("Host", "")
    return host.startswith("localhost") or host.startswith("127.0.0.1")


def get_current_user(app):
    """Get the currently authenticated Catalyst user."""
    try:
        auth_service = app.authentication()
        user = auth_service.get_current_user()
        return user
    except Exception as e:
        logger.warning(f"Failed to get current user: {e}")
        return None


def get_clinic_id(app, request=None):
    """
    Resolve the clinic_id for the current authenticated user.
    Looks up the Clinics table where admin_user_id matches the current user.
    Returns (clinic_id, user) tuple or (None, None) if not found.
    In local dev (no auth), returns the first clinic found.
    """
    user = get_current_user(app)

    # If user is authenticated, look up their clinic
    if user:
        user_id = str(user.get("user_id", ""))
        if user_id:
            try:
                zcql = app.zcql()
                result = zcql.execute_query(
                    f"SELECT ROWID FROM {TABLE_CLINICS} "
                    f"WHERE admin_user_id = '{user_id}'"
                )
                if result and len(result) > 0:
                    clinic_id = str(result[0][TABLE_CLINICS]["ROWID"])
                    return clinic_id, user
                return None, user
            except Exception as e:
                logger.error(f"Failed to resolve clinic_id: {e}")
                return None, user

    # Dev fallback ONLY for local development (catalyst serve)
    if _is_local_dev(request):
        try:
            zcql = app.zcql()
            result = zcql.execute_query(
                f"SELECT ROWID FROM {TABLE_CLINICS} LIMIT 1"
            )
            if result and len(result) > 0:
                clinic_id = str(result[0][TABLE_CLINICS]["ROWID"])
                logger.info(f"Dev mode: using first clinic {clinic_id}")
                return clinic_id, {"user_id": "dev", "email": "dev@local"}
        except Exception as e:
            logger.warning(f"Dev fallback failed: {e}")

    return None, None


def require_clinic(app, request=None):
    """
    Get clinic_id or raise an error. Use this in routes that require
    a registered clinic.
    Returns (clinic_id, user) or (None, None).
    """
    clinic_id, user = get_clinic_id(app, request)
    return clinic_id, user
