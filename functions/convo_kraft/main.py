import logging
import json
from welcome_handler import handle_welcome_request
from prompt_handler import handle_prompt_request
from fallback_handler import handle_fallback_request
from execute_handler import handle_execute_request
from failure_handler import handle_failure_request

logger = logging.getLogger(__name__)


def handler(request, response):
    handler_resp = {}

    try:
        # get_request_body() can return dict or JSON string
        req_body = request.get_request_body()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)

        todo = req_body.get('todo', '')
        logger.info(f'ConvoKraft request — todo: {todo}, body: {json.dumps(req_body)}')

        if todo == 'welcome':
            handler_resp = handle_welcome_request()
        elif todo == 'prompt':
            handler_resp = handle_prompt_request(req_body)
        elif todo == 'execute':
            handler_resp = handle_execute_request(req_body)
        elif todo == 'fallback':
            handler_resp = handle_fallback_request()
        elif todo == 'failure':
            handler_resp = handle_failure_request()
        else:
            handler_resp = {
                'message': 'Sorry, I could not process that. Please try again.'
            }

    except Exception as e:
        logger.error(f'Exception in main handler: {e}')
        handler_resp = {
            'message': 'Something went wrong. Please try again.'
        }

    response.set_status(200)
    response.set_content_type('application/json')
    response.send(json.dumps(handler_resp))
