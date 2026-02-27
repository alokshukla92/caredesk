import logging

logger = logging.getLogger(__name__)


def send_appointment_confirmation(app, patient_email, patient_name, doctor_name,
                                  clinic_name, appointment_date, appointment_time,
                                  token_number):
    """Send appointment confirmation email to patient."""
    try:
        mail = app.email()
        subject = f"Appointment Confirmed - {clinic_name}"
        content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #0d9488; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">{clinic_name}</h1>
                <p style="margin: 5px 0 0;">Appointment Confirmation</p>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been confirmed!</p>
                <div style="background: white; border-radius: 8px; padding: 16px; margin: 16px 0;">
                    <p><strong>Doctor:</strong> {doctor_name}</p>
                    <p><strong>Date:</strong> {appointment_date}</p>
                    <p><strong>Time:</strong> {appointment_time}</p>
                    <p><strong>Token Number:</strong> <span style="font-size: 24px; color: #0d9488; font-weight: bold;">{token_number}</span></p>
                </div>
                <p style="color: #64748b; font-size: 14px;">Please arrive 10 minutes before your appointment time.</p>
            </div>
        </body>
        </html>
        """
        mail.send_mail({
            "from_email": "noreply@caredesk.com",
            "to_email": patient_email,
            "subject": subject,
            "content": content,
        })
        logger.info(f"Confirmation email sent to {patient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        return False


def send_prescription_email(app, patient_email, patient_name, doctor_name,
                            clinic_name, diagnosis, medicines_text, advice):
    """Send prescription details via email."""
    try:
        mail = app.email()
        subject = f"Your Prescription - {clinic_name}"
        content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #0d9488; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">{clinic_name}</h1>
                <p style="margin: 5px 0 0;">Digital Prescription</p>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your prescription from <strong>Dr. {doctor_name}</strong>:</p>
                <div style="background: white; border-radius: 8px; padding: 16px; margin: 16px 0;">
                    <p><strong>Diagnosis:</strong> {diagnosis}</p>
                    <hr style="border: 1px solid #e2e8f0;">
                    <p><strong>Medicines:</strong></p>
                    <p>{medicines_text}</p>
                    <hr style="border: 1px solid #e2e8f0;">
                    <p><strong>Advice:</strong> {advice}</p>
                </div>
                <p style="color: #64748b; font-size: 14px;">This is a digitally generated prescription.</p>
            </div>
        </body>
        </html>
        """
        mail.send_mail({
            "from_email": "noreply@caredesk.com",
            "to_email": patient_email,
            "subject": subject,
            "content": content,
        })
        logger.info(f"Prescription email sent to {patient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send prescription email: {e}")
        return False
