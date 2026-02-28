import logging

def handle_failure_request():
    logging.info('Handling failure request')

    return {
        'message': (
            "Oops! Something went wrong. Please try again in a moment.\n\n"
            "You can also visit the CareDesk website directly to:\n"
            "- Browse clinics and book appointments\n"
            "- Track appointments using your phone number\n"
            "- Contact the clinic using their phone number"
        )
    }
