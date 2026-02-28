import logging
from utils.constants import (
    TABLE_PRESCRIPTIONS, TABLE_PATIENTS, TABLE_DOCTORS, TABLE_APPOINTMENTS,
    STATUS_BOOKED, STATUS_IN_QUEUE, STATUS_NO_SHOW,
    ist_today, ist_tomorrow,
)
from utils.response import success, server_error
from services.mail_service import send_appointment_confirmation
from services.sms_service import send_followup_reminder_sms

logger = logging.getLogger(__name__)


def send_follow_up_reminders(app, request):
    """
    GET /api/cron/follow-up-reminders
    Called by Catalyst Job Scheduling (CRON) daily.
    Sends reminder emails to patients whose follow-up date is tomorrow.
    """
    try:
        tomorrow = ist_tomorrow()
        zcql = app.zcql()

        # Find prescriptions with follow-up date = tomorrow
        result = zcql.execute_query(
            f"SELECT {TABLE_PRESCRIPTIONS}.ROWID, {TABLE_PRESCRIPTIONS}.patient_id, "
            f"{TABLE_PRESCRIPTIONS}.doctor_id, {TABLE_PRESCRIPTIONS}.follow_up_date, "
            f"{TABLE_PRESCRIPTIONS}.clinic_id, "
            f"{TABLE_PATIENTS}.name, {TABLE_PATIENTS}.email, {TABLE_PATIENTS}.phone, "
            f"{TABLE_DOCTORS}.name "
            f"FROM {TABLE_PRESCRIPTIONS} "
            f"LEFT JOIN {TABLE_PATIENTS} ON {TABLE_PRESCRIPTIONS}.patient_id = {TABLE_PATIENTS}.ROWID "
            f"LEFT JOIN {TABLE_DOCTORS} ON {TABLE_PRESCRIPTIONS}.doctor_id = {TABLE_DOCTORS}.ROWID "
            f"WHERE {TABLE_PRESCRIPTIONS}.follow_up_date = '{tomorrow}'"
        )

        sent_count = 0
        for row in (result or []):
            rx = row[TABLE_PRESCRIPTIONS]
            patient = row.get(TABLE_PATIENTS, {})
            doctor = row.get(TABLE_DOCTORS, {})

            patient_email = patient.get("email", "")
            if not patient_email:
                continue

            # Get clinic name
            clinic_id = rx.get("clinic_id", "")
            clinic_res = zcql.execute_query(
                f"SELECT name FROM Clinics WHERE ROWID = '{clinic_id}'"
            )
            clinic_name = clinic_res[0]["Clinics"]["name"] if clinic_res else "Your Clinic"

            try:
                mail = app.email()
                mail.send_mail({
                    "from_email": "noreply@catalystmailer.com",
                    "to_email": patient_email,
                    "subject": f"Follow-up Reminder - {clinic_name}",
                    "content": f"""
                    <html>
                    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
                        <div style="background:#0d9488;color:white;padding:20px;text-align:center;">
                            <h1 style="margin:0;">{clinic_name}</h1>
                            <p style="margin:5px 0 0;">Follow-up Reminder</p>
                        </div>
                        <div style="padding:20px;background:#f8fafc;">
                            <p>Dear <strong>{patient.get('name', 'Patient')}</strong>,</p>
                            <p>This is a friendly reminder that you have a follow-up appointment scheduled for <strong>{tomorrow}</strong> with <strong>Dr. {doctor.get('name', '')}</strong>.</p>
                            <p>Please book your appointment at your earliest convenience.</p>
                            <p style="color:#64748b;font-size:14px;">Wishing you good health!</p>
                        </div>
                    </body>
                    </html>
                    """,
                })
                sent_count += 1
            except Exception as mail_err:
                logger.warning(f"Follow-up mail failed for {patient_email}: {mail_err}")

            # Also send SMS reminder
            try:
                patient_phone = patient.get("phone", "")
                if patient_phone:
                    send_followup_reminder_sms(
                        patient_phone,
                        patient.get("name", ""),
                        doctor.get("name", ""),
                        tomorrow,
                        clinic_name,
                    )
            except Exception as sms_err:
                logger.warning(f"Follow-up SMS failed for {patient_phone}: {sms_err}")

        return success({
            "reminders_sent": sent_count,
            "check_date": tomorrow,
        }, f"Sent {sent_count} follow-up reminder(s)")

    except Exception as e:
        logger.error(f"Follow-up reminders cron error: {e}")
        return server_error(str(e))


def generate_daily_digest(app, request):
    """
    GET /api/cron/daily-digest
    Called by Catalyst Job Scheduling daily at end of day.
    Sends a summary email to clinic admins.
    """
    try:
        today = ist_today()
        zcql = app.zcql()

        # Get all clinics
        clinics = zcql.execute_query("SELECT ROWID, name, email FROM Clinics")
        sent_count = 0

        for row in (clinics or []):
            clinic = row["Clinics"]
            clinic_id = clinic["ROWID"]
            clinic_email = clinic.get("email", "")
            if not clinic_email:
                continue

            # Count today's stats
            total = zcql.execute_query(
                f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
                f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}'"
            )
            completed = zcql.execute_query(
                f"SELECT ROWID FROM {TABLE_APPOINTMENTS} "
                f"WHERE clinic_id = '{clinic_id}' AND appointment_date = '{today}' AND status = 'completed'"
            )

            total_count = len(total) if total else 0
            completed_count = len(completed) if completed else 0

            try:
                mail = app.email()
                mail.send_mail({
                    "from_email": "noreply@catalystmailer.com",
                    "to_email": clinic_email,
                    "subject": f"Daily Summary - {clinic.get('name', 'CareDesk')} ({today})",
                    "content": f"""
                    <html>
                    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
                        <div style="background:#0d9488;color:white;padding:20px;text-align:center;">
                            <h1 style="margin:0;">Daily Summary</h1>
                            <p style="margin:5px 0 0;">{clinic.get('name', '')} — {today}</p>
                        </div>
                        <div style="padding:20px;background:#f8fafc;">
                            <div style="background:white;border-radius:8px;padding:16px;margin:16px 0;">
                                <p><strong>Total Appointments:</strong> {total_count}</p>
                                <p><strong>Completed:</strong> {completed_count}</p>
                                <p><strong>Pending:</strong> {total_count - completed_count}</p>
                            </div>
                            <p style="color:#64748b;font-size:14px;">This is an automated daily digest from CareDesk.</p>
                        </div>
                    </body>
                    </html>
                    """,
                })
                sent_count += 1
            except Exception as mail_err:
                logger.warning(f"Digest mail failed for clinic {clinic_id}: {mail_err}")

        return success({
            "digests_sent": sent_count,
            "date": today,
        }, f"Sent {sent_count} daily digest(s)")

    except Exception as e:
        logger.error(f"Daily digest cron error: {e}")
        return server_error(str(e))


def mark_no_shows(app, request):
    """
    GET /api/cron/mark-no-shows
    Called by Catalyst Job Scheduling daily at end of day (e.g., 9 PM).
    Marks all appointments for today that are still 'booked' or 'in-queue'
    (patient never showed up or left without seeing doctor) as 'no-show'.
    """
    try:
        today = ist_today()
        zcql = app.zcql()

        # Find all stale appointments: booked or in-queue but day is over
        stale = zcql.execute_query(
            f"SELECT ROWID, status, clinic_id FROM {TABLE_APPOINTMENTS} "
            f"WHERE appointment_date = '{today}' "
            f"AND status IN ('{STATUS_BOOKED}', '{STATUS_IN_QUEUE}')"
        )

        if not stale or len(stale) == 0:
            return success({
                "marked": 0,
                "date": today,
            }, "No stale appointments found")

        table = app.datastore().table(TABLE_APPOINTMENTS)
        marked = 0
        for row in stale:
            appt = row[TABLE_APPOINTMENTS]
            try:
                table.update_row({
                    "ROWID": appt["ROWID"],
                    "status": STATUS_NO_SHOW,
                })
                marked += 1
            except Exception as upd_err:
                logger.warning(f"Failed to mark no-show for {appt['ROWID']}: {upd_err}")

        logger.info(f"Marked {marked} appointment(s) as no-show for {today}")
        return success({
            "marked": marked,
            "date": today,
        }, f"Marked {marked} appointment(s) as no-show")

    except Exception as e:
        logger.error(f"Mark no-shows cron error: {e}")
        return server_error(str(e))
