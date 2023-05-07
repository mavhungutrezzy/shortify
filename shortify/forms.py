from datetime import datetime
import wtforms as fields
from flask_wtf import FlaskForm

from . import constants as const
from . import validators as custom_validators
from wtforms import validators


class UrlMapForm(FlaskForm):
    original_link = fields.URLField(
        label="Enter long link",
        validators=(
            validators.DataRequired(message="Required Field"),
            validators.URL(message="Invalid URL"),
        ),
    )
    custom_id = fields.StringField(
        label=f"Enter a name of up to {const.MAX_LEN_SHORT} characters",
        validators=(
            validators.Optional(),
            validators.Length(
                max=const.MAX_LEN_SHORT,
                message="Name is longer than {const.MAX_LEN_SHORT}",
            ),
            custom_validators.AllOf(
                values=const.ALLOWED_SYMBOLS,
                message="Only Latin characters and numbers are allowed",
            ),
        ),
    )
    submit = fields.SubmitField(label="Create")


class RegistrationForm(FlaskForm):
    email = fields.StringField(
        "Email", [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Email")]
    )
    password = fields.PasswordField(
        "Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH,
                message=const.PASSWORD_MIN_LENGTH_MESSAGE,
            ),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = fields.PasswordField(
        "Confirm Password",
        [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password")],
    )
    submit = fields.SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = fields.StringField(
        "Email", [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Email")]
    )
    password = fields.PasswordField(
        "Password",
        [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password")],
    )
    submit = fields.SubmitField(label="Login")


class LogoutForm(FlaskForm):
    submit = fields.SubmitField(label="Logout")


class UserForm(FlaskForm):
    first_name = fields.StringField(
        "First Name",
        [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "First Name")],
    )
    last_name = fields.StringField(
        "Last Name",
        [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Last Name")],
    )
    submit = fields.SubmitField(label="Update")


class PasswordChangeForm(FlaskForm):
    old_password = fields.PasswordField(
        "Current Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH,
                message=const.PASSWORD_MIN_LENGTH_MESSAGE,
            ),
        ],
    )
    new_password = fields.PasswordField(
        "New Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH, message=const.PASSWORD_MIN_LENGTH_MESSAGE
            ),
            validators.EqualTo("confirm_password", message="Passwords must match"),
        ],
    )
    confirm_password = fields.PasswordField(
        "Repeat Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH, message=const.PASSWORD_MIN_LENGTH_MESSAGE
            ),
        ],
    )
    submit = fields.SubmitField(label="Update")


class EmailForm(FlaskForm):
    email = fields.StringField(
        "Email", [validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Email")]
    )
    submit = fields.SubmitField(label="Update")


class PasswordResetForm(FlaskForm):
    password = fields.PasswordField(
        "Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH,
                message=const.PASSWORD_MIN_LENGTH_MESSAGE,
            ),
            validators.EqualTo("confirm_password", message="Passwords must match"),
        ],
    )
    confirm_password = fields.PasswordField(
        "Repeat Password",
        [
            validators.DataRequired(message=const.NO_REQUIRED_FIELD % "Password"),
            validators.Length(
                min=const.PASSWORD_MIN_LENGTH, message=const.PASSWORD_MIN_LENGTH_MESSAGE
            ),
        ],
    )
    submit = fields.SubmitField(label="Reset Password")


class UrlSettingsForm(FlaskForm):
    suspended = fields.BooleanField("Suspend URL", validators=[validators.Optional()])
    expiration_date = fields.DateField(
        "Expiration Date", format="%Y-%m-%d", validators=[validators.Optional()]
    )

    def validate_expiration_date(self, expiration_date):
        if expiration_date.data and expiration_date.data < datetime.now().date():
            raise validators.ValidationError("Expiration date must be in the future")

    submit = fields.SubmitField(label="Update")
