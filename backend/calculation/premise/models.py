"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models

from base.models import AbstractDescription
from core.abstract.models import AbstractModel
from utils import _


class PremiseValidator(AbstractDescription):
    """
    A class representing a PremiseValidator.

    Attributes:
    """
    formula = models.TextField(_('Formula'))


class Premise(AbstractDescription):
    """
    This class represents a premise in a logical expression. It subclasses the `AbstractDescription` class and adds a
    `ManyToManyField` relationship with a `PremiseValidator` model.
    """
    formulas = models.ManyToManyField(PremiseValidator, blank=True)
