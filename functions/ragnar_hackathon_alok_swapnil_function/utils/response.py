from flask import jsonify, make_response


def success(data=None, message="Success", status_code=200):
    body = {"status": "success", "message": message}
    if data is not None:
        body["data"] = data
    return make_response(jsonify(body), status_code)


def created(data=None, message="Created"):
    return success(data=data, message=message, status_code=201)


def error(message="Something went wrong", status_code=400):
    body = {"status": "error", "message": message}
    return make_response(jsonify(body), status_code)


def not_found(message="Resource not found"):
    return error(message=message, status_code=404)


def unauthorized(message="Unauthorized"):
    return error(message=message, status_code=401)


def server_error(message="Internal server error"):
    return error(message=message, status_code=500)
