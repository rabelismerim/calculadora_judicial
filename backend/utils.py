"""Commom methods"""
import datetime
import secrets
import logging

from unidecode import unidecode

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
    """
    Helper function for creating translated docstrings.

    This function takes a string as input and returns it wrapped in a gettext_lazy() call.
    The purpose of this function is to support i18n by allowing docstrings to be translated into different languages.

    Args:
        text: A string to be translated.

    :return:
        A lazy translation object containing the translated string.
    """
    return gettext_lazy(text.lstrip())


def doc(docstring):
    """
    Decorator function for adding docstrings to functions.

    This function takes a docstring as input and returns a decorator function.
    The decorator function takes a function as input and sets its __doc__ attribute to the docstring passed to the doc function.

    Args:
        docstring: A docstring to be added to a function.

    :return:
        A decorator function that adds the input docstring to the decorated function.
    """

    def decorate(fn):
        fn.__doc__ = _(docstring.lstrip())
        return fn

    return decorate


def parse_job_id(index):
    """
    Parse a job ID from an index.

    This function takes an index as input and cleans it up to create a unique job ID.
    It removes any whitespace, replaces spaces with underscores, converts the text to lowercase and removes any diacritical marks.

    Args:
        index: A string used to generate a job ID.

    :return:
        A cleaned up string that can be used as a job ID.
    """
    if not index:
        return ''
    return unidecode(index.strip()).replace(' ', '_').lower()


def log_info(*args):
    """
    Log info messages to console and file.

    This function logs info messages to both a file and the console.
    The format of the log messages is set using the LOG_FORMAT setting in Django.
    The level of logging is set using the LOG_LEVEL setting.

    Args:
        *args: Any number of arguments to be logged as info messages.
    """
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


def get_rate_selic():
    from rates.models import RATE_SELIC_NAME, Rate
    return Rate.objects.filter(index=RATE_SELIC_NAME).first()
