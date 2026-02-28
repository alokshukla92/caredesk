import logging

logger = logging.getLogger(__name__)


def handle_prompt_request(req_body):
    logger.info('Handling prompt request')

    params_to_prompt = req_body.get('paramsToPrompt', [])

    # If no parameters left to collect, proceed to execute
    if not params_to_prompt or len(params_to_prompt) == 0:
        return {
            'todo': 'execute'
        }

    # Default: let ConvoKraft handle the prompting
    return {
        'todo': 'prompt'
    }
