import logging
from datetime import date
from utils.constants import (
    TABLE_APPOINTMENTS, TABLE_PATIENTS, TABLE_DOCTORS,
    STATUS_COMPLETED, STATUS_IN_QUEUE, STATUS_BOOKED,
)
from utils.response import success, error, server_error
from services.auth_service import require_clinic
from services.cache_service import get_dashboard_stats, set_dashboard_stats

logger = logging.getLogger(__name__)


def get_stats(app, request):
    """GET /api/dashboard/stats — Today's dashboard statistics."""
    try:
        clinic_id, user = require_clinic(app)
        if not clinic_id:
            return error("No clinic found", 403)

        today = request.args.get("date", date.today().isoformat())

        zcql = app.zcql()

        # Total appointments today
        total_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}'"
        )
        total_today = len(total_result) if total_result else 0

        # Completed today
        completed_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' "
            f"AND status = '{STATUS_COMPLETED}'"
        )
        completed = len(completed_result) if completed_result else 0

        # In queue now
        queue_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' "
            f"AND status = '{STATUS_IN_QUEUE}'"
        )
        in_queue = len(queue_result) if queue_result else 0

        # Booked (upcoming)
        booked_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' "
            f"AND status = '{STATUS_BOOKED}'"
        )
        booked = len(booked_result) if booked_result else 0

        # Total patients
        patients_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} "
            f"WHERE clinic_id = '{clinic_id}'"
        )
        total_patients = len(patients_result) if patients_result else 0

        # Total doctors
        doctors_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_DOCTORS} "
            f"WHERE clinic_id = '{clinic_id}' AND status = 'active'"
        )
        total_doctors = len(doctors_result) if doctors_result else 0

        # Average feedback score today
        feedback_result = zcql.execute_query(
            f"SELECT feedback_score FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' "
            f"AND feedback_score != ''"
        )
        feedback_scores = []
        for row in (feedback_result or []):
            try:
                score = float(row[TABLE_APPOINTMENTS]["feedback_score"])
                feedback_scores.append(score)
            except (ValueError, TypeError):
                pass
        avg_feedback = round(sum(feedback_scores) / len(feedback_scores), 1) if feedback_scores else 0

        # Sentiment breakdown
        sentiment_result = zcql.execute_query(
            f"SELECT feedback_sentiment FROM {TABLE_APPOINTMENTS} "
            f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' "
            f"AND feedback_sentiment != ''"
        )
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for row in (sentiment_result or []):
            s = row[TABLE_APPOINTMENTS].get("feedback_sentiment", "neutral")
            if s in sentiments:
                sentiments[s] += 1

        stats = {
            "date": today,
            "total_appointments_today": total_today,
            "completed": completed,
            "in_queue": in_queue,
            "booked": booked,
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "avg_feedback_score": avg_feedback,
            "sentiment_breakdown": sentiments,
        }

        # Cache the stats
        set_dashboard_stats(app, clinic_id, stats)

        return success(stats)

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return server_error(str(e))
