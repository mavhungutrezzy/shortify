"""Constants and literals for the application.
"""
from collections import namedtuple
from string import ascii_letters, digits

ALLOWED_SYMBOLS = f"{ascii_letters}{digits}"

# A tuple with field names for the UrlMap model
URL_MAP_FIELDS = namedtuple("Fields", "id original short timestamp")

# A tuple that maps API request fields to UrlMap model fields
API_REQUEST_FIELDS = URL_MAP_FIELDS(None, "url", "custom_id", None)

# A tuple that maps API response fields to UrlMap model fields
API_RESPONSE_FIELDS = URL_MAP_FIELDS(None, "url", "short_link", None)

MAX_LEN_SHORT = 16
LEN_AUTO_SHORT = 6

# used in .views
SHORT_URL_IS_BUSY = "The name %s is already taken!"
YOUR_URL_IS_READY = "Your new link is ready:"
BD_ERROR = "Could not create link"
INDEX_PAGE = "index.html"

# used in .api_views
NO_REQUEST_BODY = "Request body is missing"
NO_REQUIRED_FIELD = '"%s" is a required field!'
API_EXC_MESSAGE = "Invalid short link name specified"
NOT_FOUND = "Specified id was not found"

# password
PASSWORD_MIN_LENGTH = 8
PASSWORD_MIN_LENGTH_MESSAGE = (
    "Password must be at least {PASSWORD_MIN_LENGTH} characters"
)

EMAIL_VERIFICATION_URL = (
    "http://localhost:5000/accounts/verify-email/verify?token={token}"
)
PASSWORD_RESET_URL = "http://localhost:5000/accounts/reset-password/reset?token={token}"
NOT_VERIFIED = (
    "Your email is not verified. Please check your inbox for a verification email."
)

PASSWORD_RESET_TEMPLATE = "mail/password_reset.html"
EMAIL_VERIFICATION_TEMPLATE = "mail/email_verification.html"
