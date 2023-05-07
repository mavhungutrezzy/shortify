from datetime import datetime, timezone
from http import HTTPStatus

from flask import abort, flash, redirect, render_template, request, url_for
from flask_jwt_extended import (
    create_access_token,
    decode_token,
)
from flask_login import current_user, login_required, login_user, logout_user

from . import app
from . import constants as const
from . import forms, models, utils


@app.route("/", methods=("GET", "POST"))
@login_required
def index_view():
    form = forms.UrlMapForm()
    user = current_user.id
    if current_user.is_verified is False:
        flash(const.NOT_VERIFIED)
        return render_template("index.html", form=form)
    if form.validate_on_submit():
        original, short_url, err_message = utils.get_urls_for_map(form)
        if err_message:
            flash(err_message)
            return render_template(const.INDEX_PAGE, form=form)

        if not utils.add_url_map(original, short_url, user):
            flash(const.BD_ERROR)
            return render_template(const.INDEX_PAGE, form=form)

        flash(const.YOUR_URL_IS_READY)
        flash(short_url)
    return render_template(const.INDEX_PAGE, form=form)


@app.route("/<string:short_url>")
def mapper(short_url):
    original_url = models.UrlMap.query.filter_by(short=short_url).first()
    if original_url is None:
        abort(HTTPStatus.NOT_FOUND)
    if original_url.suspended:
        abort(HTTPStatus.GONE)
    if original_url.expiration_date and original_url.expiration_date < datetime.now(
        timezone.utc
    ):
        original_url.suspended = True
        original_url.save()
        abort(HTTPStatus.GONE)

    original_url.increment_hit_count()
    return redirect(original_url.original)


@app.route("/accounts/register", methods=("GET", "POST"))
def register():
    
    form = forms.RegistrationForm()
    
    if form.validate_on_submit():
        if models.User.query.filter_by(email=form.email.data).first():
            flash("Email address already registered")
            return render_template("accounts/register.html", form=form)

        user = models.User(email=form.email.data)
        user.set_password(form.password.data)

        access_token = create_access_token(identity=user.id)
        utils.send_email_verification(user, access_token)

        user.save()

        return redirect(url_for("login_view"))

    return render_template("accounts/register.html", form=form)


@app.route("/accounts/login", methods=("GET", "POST"))
def login_view():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index_view"))
        else:
            flash("Invalid username or password")
    return render_template("accounts/login.html", form=form)


@app.route("/accounts/logout", methods=("GET", "POST"))
@login_required
def confirm_logout():
    if request.method == "POST":
        logout_user()
        return redirect(url_for("login_view"))

    form = forms.LogoutForm()
    return render_template("accounts/logout.html", form=form)


# TODO: add unit tests
@app.route("/my-urls", methods=("GET", "POST"))
@login_required
def my_urls():
    urls = models.UrlMap.query.filter_by(user_id=current_user.id)
    return render_template("accounts/urls.html", urls=urls)


@app.route("/my-urls/<int:url_id>", methods=("GET", "POST"))
def url_details(url_id):
    url = models.UrlMap.query.get_or_404(url_id)
    form = forms.UrlSettingsForm()
    if form.validate_on_submit():
        url.suspended = not url.suspended
        url.expiration_date = form.expiration_date.data
        url.save()
        flash("URL settings updated successfully!", "success")
    return render_template("accounts/url_details.html", url=url, form=form)


# TODO: add a confirmation modal
# TODO: add unit tests
@app.route("/my-urls/delete/<int:url_id>", methods=("GET", "POST"))
@login_required
def delete_url(url_id):
    url = models.UrlMap.query.get_or_404(url_id)
    if not url.is_owned_by(current_user):
        abort(403)
    url.delete()
    return redirect(url_for("my_urls"))


@app.route("/accounts", methods=("GET", "POST"))
@login_required
def accounts():
    user_form = forms.UserForm()
    password_form = forms.PasswordChangeForm()
    email_form = forms.EmailChangeForm()

    if user_form.validate_on_submit():
        current_user.first_name = user_form.first_name.data
        current_user.last_name = user_form.last_name.data
        current_user.save()
        return redirect(url_for("accounts"))

    if password_form.validate_on_submit():
        current_user.set_password(password_form.new_password.data)
        current_user.save()
        return redirect(url_for("accounts"))

    if email_form.validate_on_submit():
        current_user.email = email_form.email.data
        current_user.save()
        return redirect(url_for("accounts"))

    return render_template(
        "accounts/accounts.html",
        user_form=user_form,
        password_form=password_form,
        email_form=email_form,
    )


# TODO: add unit tests
@app.route("/accounts/resend-verification-email", methods=("GET", "POST"))
def resend_verification_email():
    if current_user.is_authenticated:
        access_token = create_access_token(identity=current_user.id)
        utils.send_email_verification(current_user, access_token)
    return redirect(url_for("index_view"))


# TODO: add unit tests
@app.route("/accounts/verify-email/verify", methods=("GET", "POST"))
def verify_email():
    token = request.args.get("token")
    user_id = None
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token["sub"]
    except Exception:
        flash("The verification link is invalid or has expired.")
        return redirect(url_for("login_view"))
    user = models.User.query.get_or_404(user_id)
    if user.is_verified:
        flash("Account already verified. Please login.")
        return redirect(url_for("login_view"))
    user.is_verified = True
    user.save()

    flash("You have successfully verified your email address.")
    return redirect(url_for("login_view"))


# TODO: add unit tests
@app.route("/accounts/forgot-password", methods=("GET", "POST"))
def forgot_password():
    form = forms.EmailForm()
    if form.validate_on_submit():
        if user := models.User.query.filter_by(email=form.email.data).first():
            access_token = create_access_token(identity=user.id)
            utils.send_password_reset_email(user, access_token)
            flash("Password reset email sent.", "success")
            return redirect(url_for("forgot_password"))
        else:
            flash("No account with that email address exists.", "danger")

    return render_template("accounts/forgot_password.html", form=form)


# TODO: add unit tests
@app.route("/accounts/reset-password/reset", methods=("GET", "POST"))
def reset_password():
    token = request.args.get("token")
    decoded_token = decode_token(token)
    user_id = decoded_token["sub"]
    form = forms.PasswordResetForm()

    if form.validate_on_submit():
        user = models.User.query.get_or_404(user_id)
        user.set_password(form.password.data)
        user.save()

        flash("Password successfully updated.", "success")
        return redirect(url_for("reset_password_done"))

    return render_template("accounts/reset_password.html", form=form)


@app.route("/accounts/reset-password-done", methods=("GET", "POST"))
def reset_password_done():
    return render_template("accounts/reset_password_done.html")
