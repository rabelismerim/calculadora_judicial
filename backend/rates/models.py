import datetime

import pandas as pd
from django.core.validators import MinLengthValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from config.settings import RATE_FILE_TYPES

from core.abstract.models import AbstractModel
from rest_framework import serializers

from utils import _


class Rate(AbstractModel):  # Indices
    index = models.CharField(_('Rate Name'), max_length=50)
    is_per_day = models.BooleanField(_('Is the Rate per day? day or month'), default=True)

    def is_ipca_e_selic(self) -> bool:
        """
        Excel D65

        See if the rate is IPCA-E/SELIC reference the analysis sheet worksheet.
        """
        return self.index == "IPCA-E/SELIC"

    def is_tst(self) -> bool:
        """
        See if the rate is TST reference the analysis sheet worksheet.
        """
        return self.index == "TST"

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
    date = models.DateField(_('Rate date'))
    value = models.FloatField(_('Rate value'))

    def __str__(self):
        return str(_('rate: {} | date: {} | value: {}').format(self.rate, self.date, self.value))

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
    value = models.FloatField(_('Valor'))

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
    file = models.FileField(_('Rate file'), upload_to=f'juca/indices/%Y-%m-%d/')

    def __str__(self):
        return str(_("rate: {} | file: {}").format(self.rate, self.file.name))

    def save(self, *args, **kwargs):
        file_type = self.file.name.split('.')[-1]
        if file_type not in RATE_FILE_TYPES:
            raise serializers.ValidationError([_('Invalid file type')])
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
        raise ValidationError(_('The reference year must be an integer.'))
    if int(value) < 1984:
        raise ValidationError(_('The reference year must be from 1984 onwards.'))


class IndiceIRRF(AbstractModel):
    reference_year = models.CharField(_('Reference year'), max_length=4,
                                      validators=[validate_reference_year, MinLengthValidator(4)])
    start = models.FloatField(_('From'))
    end = models.FloatField(_('To'))
    aliquot = models.FloatField(_('Aliquot'))
    deduction = models.FloatField(_('Deduction'))

    def __str__(self):
        return f"{self.start} | {self.end} | {self.aliquot} | {self.deduction}"

    class Meta:
        ordering = ('created_at',)


def get_aliquot_by_tax(taxable_portion: float) -> float or None:
    return IndiceIRRF.objects.filter(start__lte=taxable_portion, end__gte=taxable_portion).first()


class Template(AbstractModel):
    """
    This class represents a template used for calculating funds. Each template has fields that store information
    about the data used in the calculation.

    Attributes:
        name (str): The template name.
    """
    name = models.CharField(_('Rates'), max_length=150)
    end_point = models.CharField(_('End Point'), max_length=150, null=True)

    def __str__(self):
        return self.name


class TemplateRate(AbstractModel):
    """
    This class represents a template used for calculating funds. Each template has fields that store information
    about the data used in the calculation.

    Attributes:
        description (str): The description name.
        end_point (str): The endpoint where the data can be accessed.
        many (bool): Whether there can be multiple instances of the template.
    """
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    description = models.CharField('Description', max_length=150)
    end_point = models.CharField(_('End Point'), max_length=150)
    many = models.BooleanField(_('Is Multiple?'))

    def __str__(self):
        return f'{self.description} | {self.template.name}'


TYPE_CHOICES = (
    ('D', 'date'),
    ('B', 'boolean'),
    ('C', 'text'),
    ('F', 'float'),
    ('I', 'integer'),
    ('T', 'datetime'),
)


class AbstractTemplateField(AbstractModel):
    """
    This class represents the fields for a template.

    Attributes:
        label (str): The name of the field.
        key (str): A unique key used to identify the field.
        type (str): The type of data stored in the field.
        order (str): The order in which the field is displayed.
        is_editable (bool): Whether the field is editable.
        required (bool): Whether the field is required.
    """
    label = models.CharField(_('Field name'), max_length=150)
    key = models.CharField(_('Field key'), max_length=150)
    type = models.CharField(_('Field type'), choices=TYPE_CHOICES, max_length=1)
    order = models.PositiveIntegerField(_('Order'))
    is_editable = models.BooleanField(_('Is editable?'))
    required = models.BooleanField(_('Required?'))

    def __str__(self):
        return self.label


class TemplateMainField(AbstractTemplateField):
    """
    This class represents the fields for a template in table

    Attributes:
        template (Template): The template the field belongs to.
        label (str): The name of the field.
        key (str): A unique key used to identify the field.
        type (str): The type of data stored in the field.
        order (str): The order in which the field is displayed.
        is_editable (bool): Whether the field is editable.
        required (bool): Whether the field is required.
    """
    template = models.ForeignKey(Template, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.label} | {self.template.name}'


class TemplateField(AbstractTemplateField):
    """
    This class represents the fields for a template main.

    Attributes:
        rate (Template): The template the field belongs to.
        label (str): The name of the field.
        key (str): A unique key used to identify the field.
        type (str): The type of data stored in the field.
        order (str): The order in which the field is displayed.
        is_editable (bool): Whether the field is editable.
        required (bool): Whether the field is required.
    """
    rate = models.ForeignKey(TemplateRate, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.label} | {self.rate.description} | {self.rate.template.name}'
