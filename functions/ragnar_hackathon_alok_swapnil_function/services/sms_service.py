"""
Twilio SMS Service for CareDesk.
Uses Twilio REST API directly via requests (no SDK needed).

Setup:
1. Sign up at https://www.twilio.com/try-twilio
2. Get your Account SID, Auth Token, and Twilio phone number
3. Replace the placeholder values below
4. In trial mode, verify recipient numbers at: https://www.twilio.com/console/phone-numbers/verified
"""

import os
import logging
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

# ── Twilio Configuration (from environment variables) ─────────────
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")

# Set to False to disable SMS (useful for dev/testing)
SMS_ENABLED = True
# ──────────────────────────────────────────────────────────────────


def _send_sms(to_phone, body):
    """Send an SMS via Twilio REST API. Returns True on success."""
    if not SMS_ENABLED:
        logger.info(f"[SMS DISABLED] To: {to_phone} | Body: {body[:80]}...")
        return False

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.warning("[SMS] Twilio credentials not configured. Skipping SMS.")
        return False

    # Ensure Indian format: +91XXXXXXXXXX
    phone = to_phone.strip()
    if not phone.startswith("+"):
        if phone.startswith("91") and len(phone) >= 12:
            phone = f"+{phone}"
        else:
            phone = f"+91{phone}"

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        response = requests.post(
            url,
            data={"To": phone, "From": TWILIO_FROM_NUMBER, "Body": body},
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
        result = response.json()

        if response.status_code in (200, 201):
            logger.info(f"[SMS SENT] To: {phone} | SID: {result.get('sid', 'N/A')}")
            return True
        else:
            logger.warning(f"[SMS FAILED] To: {phone} | Error: {result.get('message', response.text)}")
            return False

    except Exception as e:
        logger.warning(f"[SMS ERROR] To: {phone} | Exception: {e}")
        return False


def send_booking_sms(phone, patient_name, doctor_name, token, time, date, clinic_name):
    """Send appointment booking confirmation SMS."""
    body = (
        f"Hi {patient_name}! Your appointment is confirmed.\n\n"
        f"Token: {token}\n"
        f"Doctor: Dr. {doctor_name}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Clinic: {clinic_name}\n\n"
        f"Please arrive 10 mins early. - CareDesk"
    )
    return _send_sms(phone, body)


def send_prescription_sms(phone, patient_name, doctor_name, diagnosis, medicines, advice, follow_up=""):
    """Send prescription summary SMS after consultation."""
    # Build medicine list (keep it short for SMS)
    med_lines = []
    for m in (medicines or [])[:5]:  # Max 5 medicines in SMS
        name = m.get("name", "")
        dosage = m.get("dosage", "")
        duration = m.get("duration", "")
        med_lines.append(f"  - {name} ({dosage}) x {duration}")

    med_text = "\n".join(med_lines) if med_lines else "  See prescription for details"

    body = (
        f"Hi {patient_name}, your prescription from Dr. {doctor_name}:\n\n"
        f"Diagnosis: {diagnosis}\n\n"
        f"Medicines:\n{med_text}\n\n"
        f"Advice: {advice[:100]}"
    )

    if follow_up:
        body += f"\n\nFollow-up: {follow_up}"

    body += "\n\n- CareDesk"
    return _send_sms(phone, body)


def send_followup_reminder_sms(phone, patient_name, doctor_name, follow_up_date, clinic_name):
    """Send follow-up appointment reminder SMS (2 days before)."""
    body = (
        f"Hi {patient_name}! Reminder: Your follow-up with Dr. {doctor_name} "
        f"is on {follow_up_date}.\n\n"
        f"Please book your appointment at {clinic_name}.\n\n"
        f"Stay healthy! - CareDesk"
    )
    return _send_sms(phone, body)
