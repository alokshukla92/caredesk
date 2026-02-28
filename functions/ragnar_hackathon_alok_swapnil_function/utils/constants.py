# Table names in Catalyst Data Store
TABLE_CLINICS = "Clinics"
TABLE_DOCTORS = "Doctors"
TABLE_PATIENTS = "Patients"
TABLE_APPOINTMENTS = "Appointments"
TABLE_PRESCRIPTIONS = "Prescriptions"

# Appointment status flow
STATUS_BOOKED = "booked"
STATUS_IN_QUEUE = "in-queue"
STATUS_IN_CONSULTATION = "in-consultation"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"
STATUS_NO_SHOW = "no-show"

VALID_STATUSES = [
    STATUS_BOOKED,
    STATUS_IN_QUEUE,
    STATUS_IN_CONSULTATION,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    STATUS_NO_SHOW,
]

# Allowed status transitions
STATUS_TRANSITIONS = {
    STATUS_BOOKED: [STATUS_IN_QUEUE, STATUS_CANCELLED, STATUS_NO_SHOW],
    STATUS_IN_QUEUE: [STATUS_IN_CONSULTATION, STATUS_CANCELLED, STATUS_NO_SHOW],
    STATUS_IN_CONSULTATION: [STATUS_COMPLETED],
    STATUS_COMPLETED: [],
    STATUS_CANCELLED: [],
    STATUS_NO_SHOW: [],
}

# Gender options
GENDERS = ["Male", "Female", "Other"]

# Sentiment labels
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_NEUTRAL = "neutral"

# IST timezone helpers (Catalyst servers run in UTC)
from datetime import datetime, timezone, timedelta, date as _date_type

IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    """Return current datetime in IST."""
    return datetime.now(IST)

def ist_today():
    """Return today's date string (YYYY-MM-DD) in IST."""
    return ist_now().date().isoformat()

def ist_time_now():
    """Return current time string (HH:MM) in IST."""
    return ist_now().strftime("%H:%M")

def ist_tomorrow():
    """Return tomorrow's date string (YYYY-MM-DD) in IST."""
    return (ist_now().date() + timedelta(days=1)).isoformat()
