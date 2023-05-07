"""The module contains the API views.
"""
from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app
from . import constants as const
from . import utils
from .error_handlers import APIException
from .models import UrlMap
from .validators import len_validation, symbols_validation


@app.route("/api/id/", methods=["POST"])
def new_short_url():
    """The function creates a new short url.

    Raises:
        APIException: If the request body is empty.

    Returns:
        Responce: A JSON object with the short url and the original url.
    """
    data = request.get_json()

    if not data:
        raise APIException(const.NO_REQUEST_BODY)

    original = data.get(const.API_REQUEST_FIELDS.original)

    if original is None:
        raise APIException(const.NO_REQUIRED_FIELD % const.API_REQUEST_FIELDS.original)

    short = data.get(const.API_REQUEST_FIELDS.short)

    if short:
        len_validation(
            short, APIException(const.API_EXC_MESSAGE), max=const.MAX_LEN_SHORT
        )
        symbols_validation(short, APIException(const.API_EXC_MESSAGE))
        if utils.short_url_exist(short):
            raise APIException(const.SHORT_URL_IS_BUSY % short)
    else:
        short = utils.get_unique_short_id()

    utils.add_url_map(original, short)

    response_dict = {
        const.API_RESPONSE_FIELDS.short: url_for(
            "mapper", short_url=short, _external=True
        ),
        const.API_RESPONSE_FIELDS.original: original,
    }
    return jsonify(response_dict), HTTPStatus.CREATED


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def get_mapper_url(short_id):
    """The function returns the original url by short_id.

    Args:
        short_id (str): Short name.

    Raises:
        APIException: If the short_id is not found.

    Returns:
        tuple(str, int): json and HTTP status code.
    """
    url_map = UrlMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise APIException(const.NOT_FOUND, HTTPStatus.NOT_FOUND)

    response_dict = {const.API_RESPONSE_FIELDS.original: url_map.original}
    return response_dict, HTTPStatus.OK
