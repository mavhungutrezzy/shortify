"""Generic error handlers for the application

"""
from http import HTTPStatus

from flask import jsonify, render_template

from . import app


class APIException(Exception):
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def as_dict(self):
        return dict(message=self.message)


@app.errorhandler(APIException)
def api_exception(error):
    return jsonify(error.as_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    return render_template("error_pages/404.html"), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.GONE)
def url_suspended(error):
    return render_template("error_pages/410.html"), HTTPStatus.GONE
