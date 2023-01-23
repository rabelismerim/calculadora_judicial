"""Commom methods"""

from config.settings import AUTH_USER_MODEL as User
from django.contrib.auth import get_user_model as md

def get_user_model():
    """Get user Model"""
    return md()
   