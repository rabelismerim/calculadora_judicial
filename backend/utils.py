"""Commom methods"""

from django.contrib.auth import get_user_model as md
from django.utils.translation import gettext_lazy as _


def get_user_model():
    """Get user Model"""
    return md()


def check_choice(value: str, choices: tuple):
    """Checks if the status value provided is valid"""
    has_value = False
    for string, legend in choices:
        if value == string:
            has_value = True
            break
    if not has_value:
        raise ValueError(_(f'O valor {value} não corresponde a nenhuma escolha válida'))
