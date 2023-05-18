"""Commom methods"""
import datetime
import secrets
import logging
from config import settings
from django.contrib.auth import get_user_model as md
from django.utils.translation import gettext_lazy


def get_user_model():
    """Get user Model"""
    return md()


def secret_number(min_value: int, max_value: int):
    min_ = min(min_value, max_value)
    max_ = max(min_value, max_value)
    return secrets.randbelow(max_ - min_) + 1


def check_choice(value: str, choices: tuple):
    """Checks if the status value provided is valid
    Params:
        -value: str
        -choices: list of tuple
    """
    has_value = False
    for string, legend in choices:
        if value == string:
            has_value = True
            break
    if not has_value:
        raise ValueError(_('The value {} does not match any valid choice'.format(value)))


def days360(start_date, end_date) -> int:
    """Return the number of days between the start_date and end_date using the 360-day method."""
    if start_date.day == 31:
        start_date = start_date.replace(day=30)
    if end_date.day == 31 and (start_date.day == 30 or start_date.day == 31):
        end_date = end_date.replace(day=30)
    elif end_date.day == 31:
        end_date = end_date.replace(day=1)
        end_date = end_date + datetime.timedelta(days=1)
    return (end_date.year - start_date.year) * 360 + \
        (end_date.month - start_date.month) * 30 + \
        (end_date.day - start_date.day)


def _(text):
    return gettext_lazy(text.lstrip())


def doc(docstring):
    def decorate(fn):
        fn.__doc__ = _(docstring.lstrip())
        return fn

    return decorate


def log_info(*args):
    fmt = getattr(settings, 'LOG_FORMAT', None)
    lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.setLevel(lvl)

    file_handler = logging.FileHandler(settings.LOGGING['handlers']['file_info']['filename'], encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console_handler)
    for arg in args:
        logger.info(arg)
