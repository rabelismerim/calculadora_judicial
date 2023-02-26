import pandas as pd
from django.db import models
from config.settings import RATE_FILE_TYPES

from core.abstract.models import AbstractModel
from django.utils.translation import gettext as _
from rest_framework import serializers


class Rate(AbstractModel):  # Indices
    """
    Model representing a rate or index.

    Attributes:
    - index (CharField): The name of the index, with a maximum length of 50 characters.

    """
    index = models.CharField('Nome do indice', max_length=50)

    def __str__(self):
        return self.index

    def get_ratefile(self):
        if hasattr(self, 'ratefile'):
            return self.ratefile
        return None


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
    date = models.DateField('Data do indice')
    value = models.FloatField('Valor do indice')

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
