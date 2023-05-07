from wtforms import validators

from . import constants as const

DataRequired = validators.DataRequired
Length = validators.Length
Optional = validators.Optional
URL = validators.URL
ValidationErr = validators.ValidationError


def len_validation(sequense, exception, min=1, max=1):
    try:
        getattr(sequense, "__len__")
    except AttributeError as e:
        raise AttributeError from e
    if min <= len(sequense) <= max:
        return
    raise exception


def symbols_validation(string, exception):
    if isinstance(string, str) and all(
        (symbol in const.ALLOWED_SYMBOLS) for symbol in string
    ):
        return
    raise exception


class AllOf(validators.AnyOf):
    def __call__(self, form, field):
        if self.message is None:
            self.message = f"Some element of {field.data} not in {self.values}"
        symbols_validation(field.data, validators.ValidationError(self.message))
