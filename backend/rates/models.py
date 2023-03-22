import datetime

import pandas as pd
from django.core.validators import MinLengthValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from config.settings import RATE_FILE_TYPES

from core.abstract.models import AbstractModel
from django.utils.translation import gettext as _
from rest_framework import serializers


class Rate(AbstractModel):  # Indices
    index = models.CharField('Nome do índice', max_length=50)
    is_per_day = models.BooleanField('O índice é por dia? dia ou mês', default=True)

    def __str__(self):
        return self.index

    def get_ratefile(self):
        if hasattr(self, 'ratefile'):
            return self.ratefile
        return None

    def get_rate_by_date(self, date: datetime.date):
        if self.is_per_day:
            return self.ratevalues_set.filter(date=date).first()
        return self.ratevalues_set.filter(date__month=date.month, date__year=date.year).first()


class RateValues(AbstractModel):  # Indices
    """
    A model that defines a rate value for a given date and index.

    Attributes:
    ----------
    index : Rate
        The index to which this rate value belongs.
    date : datetime.date
        The date associated with the rate value.
    value : float
        The rate value for the given index and date.

    Methods:
    --------
    __str__() -> str
        Returns a string representation of the object.
    """
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)
    date = models.DateField('Data do índice')
    value = models.FloatField('Valor do índice')

    def __str__(self):
        return f"indice: {self.rate} | data: {self.date} | value: {self.value}"

    @property
    def get_period(self):
        if hasattr(self, 'period'):
            return self.period.value
        return None

    @property
    def get_accumulated(self):
        if hasattr(self, 'accumulated'):
            return self.accumulated.value
        return None


class AbstractCalcule(AbstractModel):
    """
    Abstract class that defines a model for generic calculations.

    Attributes:
    ----------
    value : float
        The value to be calculated.

    Methods:
    --------
    __str__() -> str
        Returns a string representation of the object.
    """
    value = models.FloatField('Valor')

    def __str__(self):
        return f"{self.value}"

    class Meta:
        abstract = True


class Period(AbstractCalcule):
    """
    Class that defines a model for calculations based on a period of time.

    Attributes:
    ----------
    rate : RateValues
        The interest rate to be applied to the calculation.

    Methods:
    --------
    (inherited from the AbstractCalcule class)
    """
    rate = models.OneToOneField(RateValues, on_delete=models.PROTECT)


class Accumulated(AbstractCalcule):
    """
    Class that defines a model for calculations of accumulated value.

    Attributes:
    ----------
    rate : RateValues
        The interest rate to be applied to the calculation.

    Methods:
    --------
    (inherited from the AbstractCalcule class)
    """
    rate = models.OneToOneField(RateValues, on_delete=models.PROTECT)


class RateFile(AbstractModel):
    """
    Class that defines a model for calculations of accumulated value.

    Attributes:
    ----------
    rate : RateValues
        The interest rate to be applied to the calculation.

    Methods:
    --------
    (inherited from the AbstractCalcule class)
    """
    rate = models.OneToOneField(Rate, on_delete=models.PROTECT)
    file = models.FileField('Arquivo de indices',
                            upload_to=f'djud/indices/%Y-%m-%d/')

    def __str__(self):
        return f"indice: {self.rate} | arquivo: {self.file.name}"

    def save(self, *args, **kwargs):
        file_type = self.file.name.split('.')[-1]
        if file_type not in RATE_FILE_TYPES:
            raise serializers.ValidationError(['Tipo de arquivo inválido'])
        super(RateFile, self).save(*args, **kwargs)

    def get_excel_to_dict(self):
        rows = pd.read_excel(self.file.open()).to_dict(orient='records')
        rates = []

        if len(rows) == 0:
            return rates

        if all([rows[0].get('mes'), rows[0].get('indice')]) is False:
            return False

        for row in rows:
            new_rate = {
                "rate_value": {
                    "accumulated": row.get('acumulado'),
                    "period": row.get('periodo'),
                    "date": row.get('mes').date(),
                    "value": row.get('indice')
                },
                "index": self.rate.index
            }
            rates.append(new_rate)

        return rates

    @property
    def filename(self):
        return self.file.name.split("/")[-1]

    @property
    def index(self):
        return self.rate.index


def validate_reference_year(value):
    if not value.isnumeric():
        raise ValidationError('O ano de referência deve ser um número inteiro.')
    if int(value) < 1984:
        raise ValidationError('O ano de referência deve ser a partir de 1984.')


class IndiceIRRF(AbstractModel):
    reference_year = models.CharField(_('Ano de referência'), max_length=4,
                                      validators=[validate_reference_year, MinLengthValidator(4)])
    start = models.FloatField(_('De'))
    end = models.FloatField(_('Até'))
    aliquot = models.FloatField(_('Alíquota'))
    deduction = models.FloatField(_('Dedução'))

    def __str__(self):
        return f"{self.start} | {self.end} | {self.aliquot} | {self.deduction}"

    class Meta:
        verbose_name = _("Índice IRRF")
        verbose_name_plural = _("Índices IRRF")
        ordering = ('created_at',)


def get_aliquot_by_tax(taxable_portion: float) -> float or None:
    return IndiceIRRF.objects.filter(start__lte=taxable_portion, end__gte=taxable_portion).first()
