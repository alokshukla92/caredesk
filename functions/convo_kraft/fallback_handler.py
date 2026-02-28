import logging

def handle_fallback_request():
    logging.info('Handling fallback request')

    return {
        'message': (
            "Sorry, I didn't understand that. Please pick an option below or rephrase your question:"
        ),
        'followup': {
            'suggestions': [
                {'message': 'Book an appointment'},
                {'message': 'Track my appointments'},
                {'message': 'Check queue status'},
                {'message': 'Find a clinic'},
                {'message': 'View prescription'},
                {'message': 'Give feedback'}
            ]
        }
    }
