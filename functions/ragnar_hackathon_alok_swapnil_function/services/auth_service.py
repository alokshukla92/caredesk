import logging
from utils.constants import TABLE_CLINICS

logger = logging.getLogger(__name__)


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
    """
    user = get_current_user(app)

    if not user:
        logger.warning("get_clinic_id: no authenticated user")
        return None, None

    user_id = str(user.get("user_id", ""))
    if not user_id:
        logger.warning("get_clinic_id: user has no user_id")
        return None, user

    try:
        zcql = app.zcql()
        result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_CLINICS} "
            f"WHERE admin_user_id = '{user_id}'"
        )
        if result and len(result) > 0:
            clinic_id = str(result[0][TABLE_CLINICS]["ROWID"])
            logger.info(f"get_clinic_id: user {user_id} -> clinic {clinic_id}")
            return clinic_id, user

        logger.info(f"get_clinic_id: no clinic for user {user_id}")
        return None, user
    except Exception as e:
        logger.error(f"get_clinic_id: query failed: {e}")
        return None, user


def require_clinic(app, request=None):
    """
    Get clinic_id or return None. Use this in routes that require
    a registered clinic.
    Returns (clinic_id, user) or (None, None).
    """
    clinic_id, user = get_clinic_id(app, request)
    return clinic_id, user
