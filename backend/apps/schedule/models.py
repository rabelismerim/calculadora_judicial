"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
from django.db import models
from core.abstract.models import AbstractModel
from utils import _

class Schedule(AbstractModel):
    """
    A class representing a Schedule.

    Attributes:
    """
