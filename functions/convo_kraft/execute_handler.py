import logging
import json

logger = logging.getLogger(__name__)

# Try importing Catalyst SDK for Data Store access
try:
    import zcatalyst_sdk
    HAS_CATALYST_SDK = True
except ImportError:
    HAS_CATALYST_SDK = False
    logger.warning('zcatalyst_sdk not available — DB queries will not work')

# Quick action suggestions shown after every response
QUICK_ACTIONS = {
    'suggestions': [
        {'message': 'Book an appointment'},
        {'message': 'Track my appointments'},
        {'message': 'Check queue status'},
        {'message': 'Find a clinic'},
        {'message': 'View prescription'},
        {'message': 'Give feedback'}
    ]
}


def _get_zcql():
    """Get ZCQL service from Catalyst SDK."""
    if not HAS_CATALYST_SDK:
        return None
    try:
        app = zcatalyst_sdk.initialize()
        return app.zcql()
    except Exception as e:
        logger.error(f'Failed to initialize Catalyst SDK: {e}')
        return None


def _query(zcql, query_str):
    """Execute a ZCQL query safely."""
    try:
        result = zcql.execute_query(query_str)
        return result if result else []
    except Exception as e:
        logger.error(f'ZCQL query error: {e}')
        return []


def _respond(message, custom_followup=None):
    """Build a standard response with followup suggestions."""
    resp = {'message': message}
    resp['followup'] = custom_followup if custom_followup else QUICK_ACTIONS
    return resp


def handle_execute_request(req_body):
    logger.info('Handling execute request')
    logger.info(f'Execute body: {json.dumps(req_body)}')

    action = req_body.get('action', {})
    action_name = action.get('name', '') if isinstance(action, dict) else str(action)
    params = req_body.get('params', {})

    logger.info(f'Action: {action_name}, Params: {params}')

    try:
        # Route to the correct action handler
        # Names must match ConvoKraft console action names (alphanumeric only)
        if action_name in ('listclinics', 'list_clinics'):
            return _action_list_clinics()

        elif action_name in ('clinicdetails', 'clinic_details'):
            clinic_name = params.get('clinicname', params.get('clinic_name', ''))
            return _action_clinic_details(clinic_name)

        elif action_name in ('listdoctors', 'list_doctors'):
            clinic_name = params.get('clinicname', params.get('clinic_name', ''))
            return _action_list_doctors(clinic_name)

        elif action_name in ('checkqueue', 'check_queue'):
            clinic_name = params.get('clinicname', params.get('clinic_name', ''))
            return _action_check_queue(clinic_name)

        elif action_name in ('trackappointments', 'track_appointments'):
            phone = params.get('phonenumber', params.get('phone_number', ''))
            return _action_track_appointments(phone)

        elif action_name in ('howtobook', 'how_to_book'):
            return _action_how_to_book()

        elif action_name in ('howtofeedback', 'how_to_feedback'):
            return _action_how_to_feedback()

        elif action_name in ('howtoprescription', 'how_to_prescription'):
            return _action_how_to_prescription()

        elif action_name in ('howtocancel', 'how_to_cancel'):
            return _action_how_to_cancel()

        else:
            return _respond(
                "I can help you with:\n"
                "- Finding clinics\n"
                "- Checking doctors and fees\n"
                "- Tracking appointments\n"
                "- Checking the live queue\n"
                "- Booking, feedback, and prescription guidance\n\n"
                "Pick an option below or type your question:"
            )

    except Exception as e:
        logger.error(f'Execute handler error: {e}')
        return _respond('I ran into an issue. Please try again or pick an option below:')


# ============================================================
# Action Handlers
# ============================================================

def _action_list_clinics():
    zcql = _get_zcql()
    if not zcql:
        return _respond(
            "To see all available clinics, visit the Clinics page on CareDesk.\n\n"
            "There you can:\n"
            "- Browse all clinics with address and phone\n"
            "- See number of doctors at each clinic\n"
            "- Click 'Book Now' to book an appointment\n"
            "- Click 'View Queue' to check the live queue"
        )

    results = _query(zcql, "SELECT ROWID, name, address, phone FROM Clinics ORDER BY name ASC")

    if not results:
        return _respond("No clinics are currently available on CareDesk. Please check back later.")

    lines = []
    for i, row in enumerate(results, 1):
        c = row.get('Clinics', row)
        lines.append(f"{i}. {c.get('name', 'Unknown')}\n   Address: {c.get('address', 'N/A')}\n   Phone: {c.get('phone', 'N/A')}")

    msg = "Here are the available clinics:\n\n" + "\n\n".join(lines)
    msg += "\n\nVisit the Clinics page to book an appointment."

    return _respond(msg, {
        'suggestions': [
            {'message': 'Book an appointment'},
            {'message': 'Check queue status'},
            {'message': 'Track my appointments'}
        ]
    })


def _action_clinic_details(clinic_name):
    if not clinic_name:
        return _respond("Please tell me the clinic name you want to know about.")

    zcql = _get_zcql()
    if not zcql:
        return _respond(f"Visit the Clinics page on CareDesk to see details about '{clinic_name}'.")

    results = _query(zcql, f"SELECT ROWID, name, address, phone, email FROM Clinics WHERE name LIKE '%{clinic_name}%'")
    if not results:
        return _respond(f"I couldn't find a clinic matching '{clinic_name}'. Please check the name or visit the Clinics page.")

    c = results[0].get('Clinics', results[0])
    clinic_id = c.get('ROWID', '')

    msg = f"{c.get('name', '')}\n\nAddress: {c.get('address', 'N/A')}\nPhone: {c.get('phone', 'N/A')}\nEmail: {c.get('email', 'N/A')}"

    doctors = _query(zcql,
        f"SELECT name, specialty, consultation_fee, available_from, available_to "
        f"FROM Doctors WHERE clinic_id = '{clinic_id}' AND status = 'active' ORDER BY name ASC"
    )

    if doctors:
        msg += f"\n\nDoctors ({len(doctors)}):\n"
        for row in doctors:
            d = row.get('Doctors', row)
            msg += f"- Dr. {d.get('name', '')} | {d.get('specialty', 'General')} | Rs. {d.get('consultation_fee', 'N/A')} | {d.get('available_from', '')} - {d.get('available_to', '')}\n"

    return _respond(msg, {
        'suggestions': [
            {'message': 'Book an appointment'},
            {'message': 'Check queue status'},
            {'message': 'Find a clinic'}
        ]
    })


def _action_list_doctors(clinic_name):
    if not clinic_name:
        return _respond("Which clinic's doctors would you like to see? Please tell me the clinic name.")

    zcql = _get_zcql()
    if not zcql:
        return _respond(f"Visit the Clinics page and click 'Book Now' on '{clinic_name}' to see available doctors.")

    clinics = _query(zcql, f"SELECT ROWID, name FROM Clinics WHERE name LIKE '%{clinic_name}%'")
    if not clinics:
        return _respond(f"I couldn't find a clinic matching '{clinic_name}'.")

    clinic = clinics[0].get('Clinics', clinics[0])
    doctors = _query(zcql,
        f"SELECT name, specialty, consultation_fee, available_from, available_to "
        f"FROM Doctors WHERE clinic_id = '{clinic.get('ROWID', '')}' AND status = 'active' ORDER BY name ASC"
    )

    if not doctors:
        return _respond(f"No active doctors at {clinic.get('name', '')} right now.")

    msg = f"Doctors at {clinic.get('name', '')}:\n\n"
    for i, row in enumerate(doctors, 1):
        d = row.get('Doctors', row)
        msg += f"{i}. Dr. {d.get('name', '')}\n   Specialty: {d.get('specialty', 'General Medicine')}\n   Fee: Rs. {d.get('consultation_fee', 'N/A')}\n   Hours: {d.get('available_from', 'N/A')} - {d.get('available_to', 'N/A')}\n\n"

    return _respond(msg, {
        'suggestions': [
            {'message': 'Book an appointment'},
            {'message': 'Check queue status'}
        ]
    })


def _action_check_queue(clinic_name):
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date().isoformat()

    if not clinic_name:
        return _respond("Which clinic's queue would you like to check? Please tell me the clinic name.")

    zcql = _get_zcql()
    if not zcql:
        return _respond(f"Visit the Live Queue page on CareDesk to check the queue at '{clinic_name}'.")

    clinics = _query(zcql, f"SELECT ROWID, name FROM Clinics WHERE name LIKE '%{clinic_name}%'")
    if not clinics:
        return _respond(f"I couldn't find a clinic matching '{clinic_name}'.")

    clinic = clinics[0].get('Clinics', clinics[0])
    clinic_id = clinic.get('ROWID', '')

    queue = _query(zcql,
        f"SELECT Appointments.token_number, Appointments.status, Doctors.name "
        f"FROM Appointments "
        f"LEFT JOIN Doctors ON Appointments.doctor_id = Doctors.ROWID "
        f"WHERE Appointments.clinic_id = '{clinic_id}' "
        f"AND Appointments.appointment_date = '{today}' "
        f"AND Appointments.status IN ('in-queue', 'in-consultation') "
        f"ORDER BY Appointments.token_number ASC"
    )

    if not queue:
        return _respond(f"The queue at {clinic.get('name', '')} is currently empty. No patients are waiting.")

    now_serving = []
    waiting = []
    for row in queue:
        a = row.get('Appointments', row)
        d = row.get('Doctors', {})
        token = a.get('token_number', '?')
        doctor = d.get('name', 'N/A')
        if a.get('status') == 'in-consultation':
            now_serving.append(f"Token {token} with Dr. {doctor}")
        else:
            waiting.append(f"Token {token} (Dr. {doctor})")

    msg = f"Live Queue at {clinic.get('name', '')}:\n\n"
    if now_serving:
        msg += "Now Serving:\n" + "\n".join(f"- {s}" for s in now_serving) + "\n\n"
    if waiting:
        msg += f"Waiting ({len(waiting)}):\n" + "\n".join(f"{i}. {w}" for i, w in enumerate(waiting, 1)) + "\n\n"

    msg += "For real-time updates, visit the Live Queue page."

    return _respond(msg, {
        'suggestions': [
            {'message': 'Track my appointments'},
            {'message': 'Book an appointment'}
        ]
    })


def _action_track_appointments(phone):
    if not phone:
        return _respond("Please provide your phone number so I can look up your appointments.")

    zcql = _get_zcql()
    if not zcql:
        return _respond(f"Visit the My Appointments page on CareDesk and search with: {phone}")

    patients = _query(zcql, f"SELECT ROWID, clinic_id, name FROM Patients WHERE phone = '{phone}'")
    if not patients:
        return _respond(
            f"No appointments found for {phone}.\n\n"
            "Please check:\n"
            "- Is this the same phone number you used when booking?\n"
            "- You may have used a different number\n\n"
            "Try the My Appointments page on CareDesk."
        )

    all_appts = []
    patient_name = ''
    for pat_row in patients:
        p = pat_row.get('Patients', pat_row)
        patient_name = p.get('name', '')
        patient_id = p.get('ROWID', '')
        clinic_id = p.get('clinic_id', '')

        clinic_res = _query(zcql, f"SELECT name FROM Clinics WHERE ROWID = '{clinic_id}'")
        clinic_name = clinic_res[0].get('Clinics', {}).get('name', 'Unknown') if clinic_res else 'Unknown'

        appts = _query(zcql,
            f"SELECT Appointments.appointment_date, Appointments.appointment_time, "
            f"Appointments.status, Appointments.token_number, Doctors.name "
            f"FROM Appointments "
            f"LEFT JOIN Doctors ON Appointments.doctor_id = Doctors.ROWID "
            f"WHERE Appointments.patient_id = '{patient_id}' "
            f"AND Appointments.clinic_id = '{clinic_id}' "
            f"ORDER BY Appointments.appointment_date DESC, Appointments.appointment_time DESC"
        )

        for row in appts:
            a = row.get('Appointments', row)
            d = row.get('Doctors', {})
            all_appts.append({
                'clinic': clinic_name,
                'doctor': d.get('name', 'N/A'),
                'date': a.get('appointment_date', ''),
                'time': a.get('appointment_time', ''),
                'status': a.get('status', ''),
                'token': a.get('token_number', ''),
            })

    if not all_appts:
        return _respond(f"No appointments found for {phone}.")

    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date().isoformat()

    upcoming = [a for a in all_appts if a['date'] >= today and a['status'] not in ('completed', 'cancelled', 'no-show')]
    past = [a for a in all_appts if a not in upcoming]

    msg = f"Appointments for {patient_name} ({phone}):\n\n"

    if upcoming:
        msg += "Upcoming:\n"
        for a in upcoming:
            msg += f"- Token {a['token']} | Dr. {a['doctor']} | {a['date']} {a['time']} | {a['status'].replace('-', ' ').title()} | {a['clinic']}\n"
        msg += "\n"

    if past:
        msg += "Past:\n"
        for a in past[:5]:
            msg += f"- Token {a['token']} | Dr. {a['doctor']} | {a['date']} | {a['status'].replace('-', ' ').title()} | {a['clinic']}\n"
        if len(past) > 5:
            msg += f"  ...and {len(past) - 5} more\n"

    msg += "\nVisit My Appointments for prescriptions and feedback."

    return _respond(msg, {
        'suggestions': [
            {'message': 'View prescription'},
            {'message': 'Give feedback'},
            {'message': 'Check queue status'}
        ]
    })


# ============================================================
# Static guide actions
# ============================================================

def _action_how_to_book():
    return _respond(
        "How to book an appointment:\n\n"
        "1. Go to the Clinics page\n"
        "2. Find your clinic and click 'Book Now'\n"
        "3. Select a doctor (you'll see specialty and fee)\n"
        "4. Enter your name, phone number, and age\n"
        "5. Pick a date and time (within doctor's hours)\n"
        "6. Click 'Book Appointment'\n\n"
        "You'll get a token number (e.g. A-001) as confirmation.\n"
        "No account or login needed!\n\n"
        "Rules:\n"
        "- Cannot book for past dates\n"
        "- Time must be within doctor's available hours\n"
        "- No duplicate bookings with same doctor on same date",
        {
            'suggestions': [
                {'message': 'Find a clinic'},
                {'message': 'Track my appointments'},
                {'message': 'Check queue status'}
            ]
        }
    )


def _action_how_to_feedback():
    return _respond(
        "How to give feedback:\n\n"
        "1. Go to My Appointments page\n"
        "2. Search with your phone number\n"
        "3. Find your completed appointment\n"
        "4. Click 'Give Feedback'\n"
        "5. Rate 1-5 stars and optionally add a comment\n"
        "6. Click Submit\n\n"
        "Note: Feedback can only be given once per completed appointment.",
        {
            'suggestions': [
                {'message': 'Track my appointments'},
                {'message': 'View prescription'},
                {'message': 'Book an appointment'}
            ]
        }
    )


def _action_how_to_prescription():
    return _respond(
        "How to view your prescription:\n\n"
        "1. Go to My Appointments page\n"
        "2. Search with your phone number\n"
        "3. Find your completed appointment\n"
        "4. Click 'View Prescription'\n\n"
        "Your prescription shows diagnosis, medicines with dosage, "
        "doctor's advice, and follow-up date.\n\n"
        "If you gave your email during booking, a PDF may also be emailed to you.",
        {
            'suggestions': [
                {'message': 'Track my appointments'},
                {'message': 'Give feedback'},
                {'message': 'Book an appointment'}
            ]
        }
    )


def _action_how_to_cancel():
    return _respond(
        "Appointment cancellation is managed by the clinic staff.\n\n"
        "To cancel your appointment:\n"
        "1. Find the clinic's phone number on the Clinics page\n"
        "2. Call the clinic directly\n"
        "3. Request cancellation with your name and token number\n\n"
        "Cancellation through the website is not available for patients at this time.",
        {
            'suggestions': [
                {'message': 'Find a clinic'},
                {'message': 'Book an appointment'},
                {'message': 'Track my appointments'}
            ]
        }
    )
