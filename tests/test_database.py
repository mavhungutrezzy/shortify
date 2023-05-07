from sqlalchemy import inspect

from shortify import db
from shortify.models import UrlMap, User


def test_fields(_app):
    assert db.engine.table_names() == [
        "url_map",
        "user",
    ], 'Table "url_map" is not found in the database.'
    inspector = inspect(UrlMap)
    fields = [i.key for i in inspector.mapper.column_attrs]
    assert all(
        field
        in [
            "id",
            "original",
            "short",
            "timestamp",
            "expiration_date",
            "suspended",
            "user_id",
            "hit_count",
        ]
        for field in fields
    ), (
        'The "UrlMap" model does not have all the required fields.'
        ' Check the "UrlMap" model.'
    )
    inspector = inspect(User)
    fields = [i.key for i in inspector.mapper.column_attrs]
    assert all(
        field
        in [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "timestamp",
            "is_verified",
        ]
        for field in fields
    ), (
        'The "User" model does not have all the required fields.'
        ' Check the "User" model.'
    )
