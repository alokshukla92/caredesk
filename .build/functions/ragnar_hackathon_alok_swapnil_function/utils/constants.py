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

VALID_STATUSES = [
    STATUS_BOOKED,
    STATUS_IN_QUEUE,
    STATUS_IN_CONSULTATION,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
]

# Allowed status transitions
STATUS_TRANSITIONS = {
    STATUS_BOOKED: [STATUS_IN_QUEUE, STATUS_CANCELLED],
    STATUS_IN_QUEUE: [STATUS_IN_CONSULTATION, STATUS_CANCELLED],
    STATUS_IN_CONSULTATION: [STATUS_COMPLETED],
    STATUS_COMPLETED: [],
    STATUS_CANCELLED: [],
}

# Gender options
GENDERS = ["Male", "Female", "Other"]

# Sentiment labels
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_NEUTRAL = "neutral"
