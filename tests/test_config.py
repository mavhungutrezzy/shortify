import os


def test_env_vars():
    assert os.getenv("FLASK_APP") is not None, (
        "The FLASK_APP environment variable is not set."
        "It should be set to 'shortify'"
    )


def test_config(default_app):
    assert default_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///db.sqlite3", (
        "The SQLALCHEMY_DATABASE_URI config variable is not set."
        'It should be set to "sqlite:///db.sqlite3"'
    )
    assert default_app.config["SECRET_KEY"] == os.getenv("SECRET_KEY"), (
        "The SECRET_KEY config variable is not set."
        "It should be set to the value of the SECRET_KEY environment variable"
    )
