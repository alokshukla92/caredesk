import logging

def handle_welcome_request():
    logging.info('Handling welcome request')

    return {
        'welcome_response': {
            'message': (
                "Hello! Welcome to CareDesk — your smart clinic assistant.\n\n"
                "How can I help you today? Pick an option below or type your question:"
            ),
            'followup': {
                'suggestions': [
                    {'message': 'Book an appointment'},
                    {'message': 'Track my appointments'},
                    {'message': 'Check queue status'},
                    {'message': 'Find a clinic'},
                    {'message': 'View prescription'},
                    {'message': 'Give feedback'},
                    {'message': 'Cancel appointment'}
                ]
            }
        }
    }
