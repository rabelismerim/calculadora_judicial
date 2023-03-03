"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel


class Comparative(AbstractModel):
    """
    This class is used to store a OneToOne relationship with the Calculation model.
    """
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.calculation}'


class ApprovedCalculation(AbstractModel):  # Calculo homologado
    """
    This class is used to store a OneToOne relationship with the Calculation model.
    """
    comparative = models.OneToOneField(Comparative, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.comparative}'


class UpdatedCalculation(AbstractModel):  # Calculo atualizado
    """
    This class is used to store a OneToOne relationship with the Calculation model.
    """
    comparative = models.OneToOneField(Comparative, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.comparative}'


class AbstractFields(AbstractModel):
    """
    This class is used to store a OneToOne relationship with the Calculation model.
    """
    comparative = models.ForeignKey(
        ApprovedCalculation, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.comparative}'
