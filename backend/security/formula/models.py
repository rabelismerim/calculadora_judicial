import cryptography.fernet
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from calculation.models import Calculation
from core.abstract.models import AbstractModel
from security.views import Security
from utils import _


class EncryptedCharField(models.TextField):
    """A custom TextField that encrypts sensitive data on save"""

    def get_db_prep_value(self, value, connection, prepared=False):
        """Encrypt the value before it's saved to the database"""
        if value is not None:
            security = Security()
            try:  # Check if the value is not already encrypted
                security.decrypt(value)
            except cryptography.fernet.InvalidToken:
                return security.encrypt(value)
        return value


class Formula(AbstractModel):
    """A model that represents a formula used in a calculation"""
    method = models.TextField(_('Method name'), editable=False)
    code = EncryptedCharField(_('Code'), editable=False)
    attr = models.TextField(_('Attributes'), null=True, blank=True, editable=False)

    def __str__(self):
        return self.method


class CalcFormula(AbstractModel):
    """A model that represents a calculation formula"""
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)
    formulas = models.ManyToManyField(Formula, blank=True)

    object_id = models.UUIDField()
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    content_object = GenericForeignKey()
