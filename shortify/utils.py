import random

from flask import render_template
from flask_mail import Message

from . import app
from . import constants as const
from . import db, mail
from .models import UrlMap


def get_unique_short_id(symbols=const.ALLOWED_SYMBOLS, length=const.LEN_AUTO_SHORT):
    while True:
        result = "".join([random.choice(symbols) for _ in range(length)])
        if not UrlMap.query.filter_by(short=result).first():
            return result


def short_url_exist(short_url):
    return bool(UrlMap.query.filter_by(short=short_url).first())


def add_url_map(original, short, user_id):
    url_map = UrlMap(original=original, short=short, user_id=user_id)
    db.session.add(url_map)
    db.session.commit()
    return True


def get_urls_for_map(form):
    original = form.original_link.data
    if not (short := form.custom_id.data):
        return original, get_unique_short_id(), None
    if short_url_exist(short):
        return original, short, const.SHORT_URL_IS_BUSY % short
    else:
        return original, short, None


def send_email(user, subject, template, **kwargs):
    msg = Message(
        subject=subject, 
        sender=app.config["MAIL_USERNAME"], 
        recipients=[user.email]
    )
    msg.html = render_template(template, user=user,  **kwargs)
    mail.send(msg)


def send_password_reset_email(user, token):
    reset_password_url = const.PASSWORD_RESET_URL.format(token=token)
    send_email(
        user=user,
        subject="Password Reset Request",
        template=const.PASSWORD_RESET_TEMPLATE,
        reset_password_url=reset_password_url,
    )


def send_email_verification(user, token):
    confimation_url = const.EMAIL_VERIFICATION_URL.format(token=token)
    send_email(
        user=user,
        subject="Email Verification",
        template=const.EMAIL_VERIFICATION_TEMPLATE,
        confirmation_url=confimation_url,
    )
