"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.funds.models import Funds
from calculation.statement.models import Statement
from core.abstract.models import AbstractModel
from utils import _


# TODO: Tabela estatica. Calcular no evento signals.post.save ou em Procedure
class StatementPJ(AbstractModel):
    """
    A class representing a statement for a legal entity (PJ).

    Attributes:
        statement (Statement): The statement associated with this object.
        value (float): The total value of the statement.
        corrected_value (float): The corrected value of the statement.
        interest (float): The interest charged on the statement.
        fine (float): The fine charged on the statement.
        amount_due (float): The amount due on the statement.
    """
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)
    value = models.FloatField(_('Updated total'), default=0)
    corrected_value = models.FloatField(_('Total due'), default=0)
    interest = models.FloatField(_('Interest'), default=0)
    fine = models.FloatField(_('Fine'), default=0)
    amount_due = models.FloatField(_('Total due'), default=0)


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class FundsDescriptionPJ(AbstractModel):
    """
    A class representing a description of funds associated with a statement for a legal entity (PJ).

    Attributes:
        funds (Funds): The funds associated with this object.
        statement_pj (StatementPJ): The statement associated with this object.
    """
    funds = models.OneToOneField(Funds, on_delete=models.PROTECT)
    statement_pj = models.ForeignKey(StatementPJ, on_delete=models.PROTECT)
