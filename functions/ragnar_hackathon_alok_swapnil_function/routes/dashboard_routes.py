import logging
from collections import defaultdict
from datetime import timedelta, date as _date_type
from utils.constants import (
    TABLE_APPOINTMENTS, TABLE_PATIENTS, TABLE_DOCTORS, TABLE_PRESCRIPTIONS,
    STATUS_COMPLETED, STATUS_IN_QUEUE, STATUS_BOOKED,
    STATUS_CANCELLED, STATUS_NO_SHOW, STATUS_IN_CONSULTATION,
    ist_today, ist_now,
)
from utils.response import success, error, server_error
from services.auth_service import require_clinic

logger = logging.getLogger(__name__)


def get_stats(app, request):
    """GET /api/dashboard/stats — Rich dashboard statistics."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        today = request.args.get("date", ist_today())
        zcql = app.zcql()

        # ── 1. All appointments for the selected date (single query) ──
        day_result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.status, "
            f"{TABLE_APPOINTMENTS}.appointment_time, {TABLE_APPOINTMENTS}.doctor_id, "
            f"{TABLE_APPOINTMENTS}.patient_id, "
            f"{TABLE_APPOINTMENTS}.feedback_score, {TABLE_APPOINTMENTS}.feedback_sentiment, "
            f"{TABLE_DOCTORS}.name "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.appointment_date = '{today}'"
        )

        # Status counts
        status_counts = defaultdict(int)
        doctor_map = {}  # doctor_id -> {name, completed, total, in_consultation}
        hour_counts = defaultdict(int)  # hour -> count (for peak hours)
        feedback_scores = []
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}

        for row in (day_result or []):
            a = row[TABLE_APPOINTMENTS]
            d = row.get(TABLE_DOCTORS, {})
            status = a.get("status", "")
            status_counts[status] += 1

            # Doctor-wise breakdown
            doc_id = a.get("doctor_id", "")
            doc_name = d.get("name", "Unknown")
            if doc_id:
                if doc_id not in doctor_map:
                    doctor_map[doc_id] = {"name": doc_name, "total": 0, "completed": 0, "in_consultation": False}
                doctor_map[doc_id]["total"] += 1
                if status == STATUS_COMPLETED:
                    doctor_map[doc_id]["completed"] += 1
                if status == STATUS_IN_CONSULTATION:
                    doctor_map[doc_id]["in_consultation"] = True

            # Peak hours
            appt_time = a.get("appointment_time", "")
            if appt_time and ":" in appt_time:
                hour = appt_time.split(":")[0]
                hour_counts[hour] += 1

            # Feedback
            score_str = a.get("feedback_score", "")
            if score_str:
                try:
                    feedback_scores.append(float(score_str))
                except (ValueError, TypeError):
                    pass
            sentiment = a.get("feedback_sentiment", "")
            if sentiment in sentiments:
                sentiments[sentiment] += 1

        total_today = sum(status_counts.values())
        completed = status_counts.get(STATUS_COMPLETED, 0)
        in_queue = status_counts.get(STATUS_IN_QUEUE, 0)
        booked = status_counts.get(STATUS_BOOKED, 0)
        in_consultation = status_counts.get(STATUS_IN_CONSULTATION, 0)
        cancelled = status_counts.get(STATUS_CANCELLED, 0)
        no_show = status_counts.get(STATUS_NO_SHOW, 0)

        avg_feedback = round(sum(feedback_scores) / len(feedback_scores), 1) if feedback_scores else 0

        # Completion rate
        completion_rate = round((completed / total_today * 100), 0) if total_today > 0 else 0

        # ── 2. Total patients & doctors (lifetime) ──
        patients_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_PATIENTS} WHERE clinic_id = '{clinic_id}'"
        )
        total_patients = len(patients_result) if patients_result else 0

        doctors_result = zcql.execute_query(
            f"SELECT ROWID FROM {TABLE_DOCTORS} "
            f"WHERE clinic_id = '{clinic_id}' AND status = 'active'"
        )
        total_doctors = len(doctors_result) if doctors_result else 0

        # ── 3. Prescriptions today (via appointment date) ──
        rx_result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_APPOINTMENTS} ON {TABLE_PRESCRIPTIONS}.appointment_id = {TABLE_APPOINTMENTS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.appointment_date = '{today}'"
        )
        prescriptions_today = len(rx_result) if rx_result else 0

        # ── 4. Doctor performance list ──
        doctor_performance = []
        for doc_id, info in doctor_map.items():
            doctor_performance.append({
                "id": doc_id,
                "name": info["name"],
                "total": info["total"],
                "completed": info["completed"],
                "in_consultation": info["in_consultation"],
            })
        doctor_performance.sort(key=lambda x: x["total"], reverse=True)

        # ── 5. Peak hours (sorted) ──
        peak_hours = []
        for hour in sorted(hour_counts.keys()):
            h = int(hour)
            label = f"{h:02d}:00"
            peak_hours.append({"hour": label, "count": hour_counts[hour]})

        # ── 6. Recent activity (today's appointments with patient names) ──
        recent_result = zcql.execute_query(
            f"SELECT {TABLE_APPOINTMENTS}.ROWID, {TABLE_APPOINTMENTS}.status, "
            f"{TABLE_APPOINTMENTS}.appointment_time, {TABLE_APPOINTMENTS}.token_number, "
            f"{TABLE_DOCTORS}.name, {TABLE_PATIENTS}.name "
            f"FROM {TABLE_APPOINTMENTS} "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_APPOINTMENTS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_APPOINTMENTS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"WHERE {TABLE_APPOINTMENTS}.clinic_id = '{clinic_id}' "
            f"AND {TABLE_APPOINTMENTS}.appointment_date = '{today}' "
            f"ORDER BY {TABLE_APPOINTMENTS}.MODIFIEDTIME DESC"
        )
        recent_activity = []
        for row in (recent_result or [])[:8]:
            a = row[TABLE_APPOINTMENTS]
            recent_activity.append({
                "id": a["ROWID"],
                "patient_name": row.get(TABLE_PATIENTS, {}).get("name", ""),
                "doctor_name": row.get(TABLE_DOCTORS, {}).get("name", ""),
                "status": a.get("status", ""),
                "token_number": a.get("token_number", ""),
                "appointment_time": a.get("appointment_time", ""),
            })

        # ── 7. Weekly trend (last 7 days appointment counts) ──
        base_date = ist_now().date()
        try:
            parts = today.split("-")
            base_date = _date_type(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            pass

        weekly_trend = []
        for i in range(6, -1, -1):
            d = (base_date - timedelta(days=i)).isoformat()
            day_label = (base_date - timedelta(days=i)).strftime("%a")
            if d == today:
                # We already have today's count
                weekly_trend.append({"date": d, "day": day_label, "count": total_today})
            else:
                try:
                    r = zcql.execute_query(
                        f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
                        f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{d}'"
                    )
                    weekly_trend.append({"date": d, "day": day_label, "count": len(r) if r else 0})
                except Exception:
                    weekly_trend.append({"date": d, "day": day_label, "count": 0})

        stats = {
            "date": today,
            # Core stats
            "total_appointments_today": total_today,
            "completed": completed,
            "in_queue": in_queue,
            "booked": booked,
            "in_consultation": in_consultation,
            "cancelled": cancelled,
            "no_show": no_show,
            "completion_rate": completion_rate,
            # Totals
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "prescriptions_today": prescriptions_today,
            # Feedback
            "avg_feedback_score": avg_feedback,
            "total_feedback_count": len(feedback_scores),
            "sentiment_breakdown": sentiments,
            # Breakdown data
            "doctor_performance": doctor_performance,
            "peak_hours": peak_hours,
            "recent_activity": recent_activity,
            "weekly_trend": weekly_trend,
        }

        return success(stats)

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return server_error(str(e))
