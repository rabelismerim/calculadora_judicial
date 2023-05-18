"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models

from calculation.models import CHOICES_STEP, Calculation
from core.abstract.models import AbstractModel
from utils import _


class Comment(AbstractModel):
    """
    A class representing a Comment.

    Attributes:
        text(TextField)
    """
    text = models.TextField(_('Comment'))


class StepComment(AbstractModel):
    """
    A class representing a StepComment.

    Attributes:
        comments(ManyToManyField)
        step(CharField)
        calculation(ForeignKey)
    """
    comments = models.ManyToManyField(Comment, blank=True)
    step = models.CharField(_('Step'), max_length=1, choices=CHOICES_STEP)
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)
