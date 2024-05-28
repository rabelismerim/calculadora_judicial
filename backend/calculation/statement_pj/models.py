"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import logging

from django.db import models
from django.dispatch import receiver

from base.views import ExtractFormula
from calculation.comparative.signals import gen_statement_total_documents
from calculation.funds.document.models import TotalValuesDocument
from calculation.statement.models import Statement
from core.abstract.models import AbstractModel
from utils import _


# TODO alterar PJ para englobar documentos quando PJ, acordos PF
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

    def get_documents(self):
        """Get all legal entity documents."""
        return self.fundsdocumentdescriptionpj_set.all()

    def set_total(self, commit=True):
        """Calculate the amounts, interest, fine and days by adding all the documents of the legal entity."""
        self.value = 0
        self.corrected_value = 0
        self.interest = 0
        self.fine = 0
        self.amount_due = 0
        fund_documents = self.get_documents()
        for fund_document in fund_documents:
            document = fund_document.document
            self.value += document.total_historical
            self.corrected_value += document.total_corrected
            self.interest += document.total_default_interest
            self.fine += document.total_fine
            self.amount_due += document.total_due
        if commit:
            self.save()
        self.statement.calculation.creditor.set_total()

    def save(self, *args, **kwargs):
        self.set_total(commit=False)
        super(StatementPJ, self).save(*args, **kwargs)


class FundsDocumentDescriptionPJ(AbstractModel):
    """
    A class representing a description of funds associated with a statement for a legal entity (PJ).

    Attributes:
        document (TotalValuesDocument): The funds associated with this object.
        statement_pj (StatementPJ): The statement associated with this object.
    """
    document = models.OneToOneField(TotalValuesDocument, on_delete=models.PROTECT)
    statement_pj = models.ForeignKey(StatementPJ, on_delete=models.PROTECT)


@receiver(gen_statement_total_documents, sender=TotalValuesDocument)
def save_statement_total_documents(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementDocument object is saved. It
    calculates the monetary correction for the instance and generates the total document of the related fund. It
    takes the sender and instance as arguments
    """
    logging.info('Signal gerar fund extrato verbas documentos\n')
    statement, created = Statement.objects.get_or_create(calculation=instance.fund.calculation)
    statement_pj, created = StatementPJ.objects.get_or_create(statement=statement)
    fund, created = FundsDocumentDescriptionPJ.objects.get_or_create(document=instance, statement_pj=statement_pj)
    fund.statement_pj.set_total()

    statement_methods = ['set_total', 'get_documents']
    ExtractFormula(instance, instance.fund.calculation, statement_methods).get_methods(
        [StatementPJ, save_statement_total_documents])
