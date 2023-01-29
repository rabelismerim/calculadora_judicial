"""Commom methods"""

from django.contrib.auth import get_user_model as md

def get_user_model():
    """Get user Model"""
    return md()
   