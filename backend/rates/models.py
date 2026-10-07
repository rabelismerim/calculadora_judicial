import calendar
import datetime
import json
import logging

import pandas as pd
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Sum, TextChoices
from rest_framework.exceptions import ValidationError

from apps.schedule.views import SCHEDULER
from config.settings import RATE_FILE_TYPES

from core.abstract.models import AbstractModel
from rest_framework import serializers

from creditors.classes.models import Classes
from utils import _, parse_job_id

UNIT_CHOICES = (
    ('D', 'a.d'),
    ('M', 'a.m'),
    ('Y', 'a.a'),
)
PERIODICITY_CHOICES = (
    ('D', 'Day'),
    ('M', 'Month'),
    ('Y', 'Year'),
    ('T', 'Quarterly'),
    ('Q', 'Quarterly'),
)


class Unit(AbstractModel):  # Indices
    description = models.CharField(_('Description'), max_length=150)


class Source(AbstractModel):  # Indices
    url = models.URLField(_('Url'))
    description = models.CharField(_('Description'), max_length=150)


RATE_SELIC_NAME = 'SELIC'


class Rate(AbstractModel):  # Indices
    """
    Model for representing rates.

    This model represents a rate object that includes information such as the rate name, whether it's per day or per month, if it's active or not, and other metadata fields.
    It inherits from the AbstractModel class.

    Attributes:
        index (models.CharField): The name of the rate, represented as a character field with a maximum length of 100.
        is_per_day (models.BooleanField): A boolean value indicating whether the rate is calculated per day or per month.
        is_active (models.BooleanField): A boolean value indicating whether the rate is active.
        is_auto_update (models.BooleanField): A boolean value indicating whether the rate is set to auto-update.
        last_update (models.DateTimeField): The date and time of the last rate update, represented as a DateTimeField.
        code (models.IntegerField): An integer code for the rate.
        description (models.CharField): A brief description of the rate, represented as a character field with a maximum length of 150.
        unit (models.ForeignKey): A foreign key to the Unit model, representing the unit of measurement for the rate.
        periodicity (models.CharField): A character field representing the periodicity of the rate.
        start_date (models.DateField): A date representing the start date of the rate.
        end_date (models.DateField): A date representing the end date of the rate.
        source (models.ForeignKey): A foreign key to the Source model, representing the source of the rate data.
    """
    index = models.CharField(_('Rate Name'), max_length=100)
    is_per_day = models.BooleanField(_('Is the Rate per day? day or month'), default=True)
    is_active = models.BooleanField(_('Rate is active?'), default=True)
    is_auto_update = models.BooleanField(_('Is auto update?'), default=False)
    last_update = models.DateTimeField(_('Last update'), null=True, blank=True)

    code = models.IntegerField(_('Code'), default=0)
    description = models.CharField(_('Description'), max_length=150, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    periodicity = models.CharField(_('Periodicity'), max_length=1, choices=PERIODICITY_CHOICES, default='D')
    start_date = models.DateField(_('Fee start date'), null=True, blank=True)
    end_date = models.DateField(_('Fee end date'), null=True, blank=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, null=True, blank=True)
    # initial_accumulated = models.DecimalField(max_digits=30, decimal_places=30, null=True, blank=True, default=None)
    initial_accumulated = models.FloatField(null=True, blank=True, default=None)

    average = models.ManyToManyField('self', blank=True)  # Usado para calcular a media entre indices
    start_indice = models.DateField("Data de inicio das medias", null=True,
                                    blank=True)  # A data inicial para calcular a media

    def __init__(self, *args, **kwargs):
        """
        Construct a new Rate object.

        This method constructs a new Rate object by calling the constructor of the superclass (AbstractModel) and initializing
        a job attribute which represents the associated scheduled job for this Rate object.
        """
        super().__init__(*args, **kwargs)
        self.job = SCHEDULER.get_job(parse_job_id(self.index))

    @property
    def total_rate_values(self):
        return self.ratevalues_set.all().count()

    @property
    def scheduler_status(self):
        """
        Get the status of the associated scheduled job.

        This property returns the status of the associated scheduled job as a string indicating the next scheduled run time.
        If there is no job associated with the Rate object, it returns 'Inactive'.

        :return:
            str: The status of the associated scheduled job.
        """

        if self.job:
            if self.job.next_run_time:
                return self.job.next_run_time
            return 'Paused'
        return 'Inactive'

    @property
    def scheduler_description(self):
        """
        Get the description of the associated scheduled job.

        This property returns the description of the associated scheduled job if there is one, or '_' if there isn't.

        :return:
            str: The description of the associated scheduled job.
        """
        return self.job.description if self.job else '_'

    def is_ipca_e_selic(self) -> bool:
        """
        Excel D65

        See if the rate is IPCA-E/SELIC reference the analysis sheet worksheet.
        """
        return self.index.startswith("IPCA-E/SELIC")

    def is_ipca_e_selic_composta(self) -> bool:
        """
        Verificar se a Taxa selic é do tipo composta
        """
        return self.is_ipca_e_selic() and self.index.endswith("COMPOSTA")

    def is_tst(self) -> bool:
        """
        See if the rate is TST reference the analysis sheet worksheet.
        """
        return self.index == "TST"

    def __str__(self):
        return self.index

    def get_ratefile(self):
        """
        Get the rate file associated with the Rate object.

        This method returns the ratefile associated with the Rate object if it exists, or None otherwise.

        :return:
            RateFile or None: The ratefile associated with the Rate object.
        """
        if hasattr(self, 'ratefile'):
            return self.ratefile
        return None

    def get_rate_by_date(self, date: datetime.date):
        """
        Get the rate values for a specific date.

        This method returns the rate values associated with the Rate object for a specific date.

        Args:
            date (datetime.date): The date to get the rate values for.

        :return:
            RateValues or None: The rate values associated with the Rate object for the given date, or None if no
            rate values are found.
        """
        if self.is_per_day:
            return self.ratevalues_set.filter(date=date).first()
        return self.ratevalues_set.filter(date__month=date.month, date__year=date.year).first()

    def get_last_date(self) -> datetime.date or None:
        """
        Get the date of the last rate value.

        This method returns the date of the last rate value associated with the Rate object.

        :return:
            RateValues or None: The latest rate values associated with the Rate object for the given date, or None if no
            rate values are found.
        """
        if self.ratevalues_set.exists():
            return self.ratevalues_set.latest('date').date

    def get_first_date(self) -> datetime.date or None:
        """
        Get the date of the last rate value.

        This method returns the date of the last rate value associated with the Rate object.

        :return:
            RateValues or None: The earliest rate values associated with the Rate object for the given date, or None if no
            rate values are found.
        """
        if self.ratevalues_set.exists():
            return self.ratevalues_set.earliest('date').date

    def get_rate_by_range_dates(self, start_date, end_date):
        """
        Retrieve rate values within a specified range of dates.

        Args:
        - start_date (datetime): The start date of the range.
        - end_date (datetime): The end date of the range.

        Returns:
        - QuerySet: Rate values within the specified date range.
        """
        start_date = start_date.replace(day=1) + datetime.timedelta(days=32)
        start_date = start_date.replace(day=1)
        end_date = end_date.replace(day=1) - datetime.timedelta(days=1)
        return self.ratevalues_set.filter(date__range=[start_date, end_date])


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
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE)
    date = models.DateField(_('Rate date'), db_index=True)
    value = models.FloatField(_('Rate value'))

    def __str__(self):
        return str(_('rate: {} | date: {} | value: {}').format(self.rate, self.date, self.value))

    class Meta:
        ordering = ['-date', '-created_at', '-updated_at']

    @property
    def get_period(self):
        if hasattr(self, 'period'):
            return self.period.value
        return None

    @property
    def get_accumulated(self):
        # only use if is_ipca_e_selic
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
        ordering = ('-created_at', '-updated_at')


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
    rate = models.OneToOneField(RateValues, on_delete=models.CASCADE)


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
    rate = models.OneToOneField(RateValues, on_delete=models.CASCADE)


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
    rate = models.OneToOneField(Rate, on_delete=models.CASCADE)
    file = models.FileField(_('Rate file'), upload_to=f'calculadora-judicial/indices/%Y-%m-%d/')

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
        raise ValidationError(
            _('The reference year must be from 1984 onwards.'))


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
    rates = models.ManyToManyField(Rate, blank=True)

    def __str__(self):
        return self.name


class TemplateSlugChoices(TextChoices):
    FUNDS = 'F', 'Funds'
    FUNDS_INTEGRATION = 'I', 'Funds Integration'
    DOCUMENT = 'D', 'Document'
    Danos = 'A', 'Danos'
    IRRF = 'R', 'IRRF'
    DEDUCTION = 'E', 'Deduction'


class TemplateRate(AbstractModel):
    """
    This class represents a template used for calculating funds. Each template has fields that store information
    about the data used in the calculation.

    Attributes:
        description (str): The description name.
        end_point (str): The endpoint where the data can be accessed.
        many (bool): Whether there can be multiple instances of the template.
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    description = models.CharField('Description', max_length=150)
    end_point = models.CharField(_('End Point'), max_length=150)
    is_horizontal = models.BooleanField(_('Is Horizontal'), default=True)
    has_commit = models.BooleanField(_('Commit option'), default=True)
    many = models.BooleanField(_('Is Multiple?'))
    slug = models.CharField(_('Slug'), max_length=1, choices=TemplateSlugChoices.choices,
                            default=TemplateSlugChoices.FUNDS)

    def __str__(self):
        return f'{self.description} | {self.template.name}'


class FieldTypeChoices(TextChoices):
    DATE = 'D', 'date'
    BOOLEAN = 'B', 'boolean'
    TEXT = 'C', 'text'
    FLOAT = 'F', 'float'
    INTEGER = 'I', 'integer'
    DATETIME = 'T', 'datetime'
    CHOICES = 'H', 'choice'


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
    label = models.CharField(_('Field name'), max_length=150, null=True, blank=True)
    key = models.CharField(_('Field key'), max_length=150, null=True, blank=True)
    type = models.CharField(_('Field type'), choices=FieldTypeChoices.choices, max_length=1)
    order = models.PositiveIntegerField(_('Order'))
    is_editable = models.BooleanField(_('Is editable?'))
    required = models.BooleanField(_('Required?'))

    def __str__(self):
        return self.label or self.key or self.order

    def decimals(self) -> int:
        if self.type == 'F':
            return 6 if self.key in ['monetary_correction.index_recovering',
                                     'monetary_correction.index_data_base'] else 2
        return 0

    class Meta:
        ordering = ('order',)


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
    template = models.ForeignKey(Template, on_delete=models.CASCADE, null=True)

    def get_default(self, *args, **kwargs):
        if hasattr(self, 'templatemainfielddefault'):
            return self.templatemainfielddefault.get_value()

    @property
    def default(self):
        return self.get_default()

    def __str__(self):
        return f'{self.label} | {self.template.name}'

    def choices(self):
        choices = getattr(self, 'templatemainfieldchoices', None)
        if choices:
            return choices.choices


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
    rate = models.ForeignKey(TemplateRate, on_delete=models.CASCADE, null=True)

    def get_default(self, *args, **kwargs):
        if hasattr(self, 'templatefielddefault'):
            return self.templatefielddefault.get_value()

    def __str__(self):
        return f'{self.label} | {self.rate.description} | {self.rate.template.name}'

    def choices(self):
        choices = getattr(self, 'templatefieldchoices', None)
        if choices:
            return choices.choices


class AbstractDefault(AbstractModel):
    """
    This class represents the fields for a template main.

    Attributes:
        field (TemplateField): The TemplateField the field belongs to.
        label (str): The name of the field.
        value (text): The value of the field.
    """
    label = models.CharField(_('Original value'), max_length=150)
    value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.label} - {self.value}'

    def get_value(self):
        return json.loads(self.value).get('data')

    def set_value(self):
        self.value = json.dumps({'data': self.label})

    class Meta:
        ordering = ('created_at',)


class TemplateMainFieldDefault(AbstractDefault):
    """
    This class represents the fields for a template main.

    Attributes:
        field (TemplateField): The TemplateField the field belongs to.
    """
    field = models.OneToOneField(TemplateMainField, on_delete=models.CASCADE)


class TemplateFieldDefault(AbstractDefault):
    """
    This class represents the fields for a template main.

    Attributes:
        field (TemplateField): The TemplateField the field belongs to.
    """
    field = models.OneToOneField(TemplateField, on_delete=models.CASCADE)


class TemplateMainFieldChoices(AbstractModel):
    """
    This class represents the fields for a template main.

    Attributes:
        field (TemplateField): The TemplateField the field belongs to.
    """
    field = models.OneToOneField(TemplateMainField, on_delete=models.CASCADE)
    choices = models.JSONField()


class TemplateFieldChoices(AbstractModel):
    """
    This class represents the fields for a template main.

    Attributes:
        field (TemplateField): The TemplateField the field belongs to.
    """
    field = models.OneToOneField(TemplateField, on_delete=models.CASCADE)
    choices = models.JSONField()


class TemplateMainSummaryField(AbstractTemplateField):
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
    template = models.ForeignKey(Template, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.label} | {self.template.name}'


class TemplateSummaryField(AbstractTemplateField):
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
    rate = models.ForeignKey(TemplateRate, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.label or self.key or self.order


class CalculeRate:

    def __init__(self, filling_date: str or datetime.date, data_rj, rate_selic, rate_used):
        if isinstance(filling_date, str):
            filling_date = datetime.datetime.strptime(filling_date, '%Y-%m-%d')
        if isinstance(data_rj, str):
            data_rj = datetime.datetime.strptime(data_rj, '%Y-%m-%d')

        self.filling_date: datetime.date = filling_date
        self.data_rj: datetime.date = data_rj
        self.rate_selic: Rate = rate_selic
        self.rate_used: Rate = rate_used

    def calcule(self):
        logging.info(self.rate_used.index, 'name\n')
        if str(self.rate_used.index).upper().endswith('RECEITA-FEDERAL'):
            return self.calcule_receita_federal()

        elif str(self.rate_used.index).upper().endswith('COMPOSTA'):
            return self.calcule_composto()

        elif str(self.rate_used.index).upper().endswith('SIMPLES'):
            return self.calcule_simples()
        else:
            logging.info('indice SELIC nao encontrado')
            return self.calcule_receita_federal()

    def calcule_simples(self):
        # Converting string dates to datetime objects

        last_day_month_filling_date = calendar.monthrange(self.filling_date.year, self.filling_date.month)[1]
        # Getting the accumulated rate for the filling_date from the Rate object
        accumulated_filling_date = self.rate_selic.get_rate_by_date(self.filling_date).value

        # Calculating the accumulated rate between filling_date and the end of the month
        accumulated_interval_filling_rj = (accumulated_filling_date / 100) / last_day_month_filling_date * (
                last_day_month_filling_date - self.filling_date.day)

        # Calculating the accumulated rate within the given period (filling_date to data_rj)
        range_rates = self.rate_selic.get_rate_by_range_dates(self.filling_date, self.data_rj)

        accumulated_in_period = \
            (range_rates.order_by('date').aggregate(
                total=Sum('value'))['total'] or 0) / 100

        # Aplicar a taxa proporcional aos dias no mês
        accumulated_rj_date = self.rate_selic.get_rate_by_date(self.data_rj).value

        last_day_month_rj_date = calendar.monthrange(self.data_rj.year, self.data_rj.month)[1]

        accumulated_interval_rj_date = (accumulated_rj_date / 100) / last_day_month_rj_date * self.data_rj.day

        logging.info(accumulated_rj_date, 'accumulated_rj_date')
        logging.info(last_day_month_rj_date, 'last_day_month_rj_date')
        logging.info(self.data_rj, 'self.data_rj.month')
        logging.info(self.data_rj.day, 'self.data_rj.day\n')
        # Calculating the final SELIC rate for the period
        rate_selic_in_period = (accumulated_in_period + accumulated_interval_filling_rj + accumulated_interval_rj_date)

        # Printing the SELIC rate for the period
        logging.info(rate_selic_in_period, 'taxa_selic_no_periodo')
        logging.info(accumulated_in_period, 'accumulated_in_period')
        logging.info(accumulated_interval_filling_rj, 'accumulated_interval_filling_rj')
        logging.info(accumulated_interval_rj_date, 'accumulated_interval_rj_date')
        return rate_selic_in_period * 100

    def calcule_receita_federal(self):
        # Converting string dates to datetime objects

        last_day_month_filling_date = calendar.monthrange(self.filling_date.year, self.filling_date.month)[1]
        # Getting the accumulated rate for the filling_date from the Rate object
        accumulated_filling_date = self.rate_selic.get_rate_by_date(self.filling_date).value

        # Calculating the accumulated rate between filling_date and the end of the month
        accumulated_interval_filling_rj = (accumulated_filling_date / 100) / last_day_month_filling_date * (
                last_day_month_filling_date - self.filling_date.day)

        # Calculating the accumulated rate within the given period (filling_date to data_rj)
        range_rates = self.rate_selic.get_rate_by_range_dates(self.filling_date, self.data_rj)

        accumulated_in_period = \
            (range_rates.order_by('date').aggregate(
                total=Sum('value'))['total'] or 0) / 100

        # Calculating the final SELIC rate for the period
        rate_selic_in_period = (accumulated_in_period + accumulated_interval_filling_rj)
        logging.info(rate_selic_in_period, 'taxa_selic_no_periodo antes da porcentagem')

        # aplicar 1% referente a regra de no mês da RJ ser 1%
        rate_selic_in_period = rate_selic_in_period + (1 / 100)

        # Printing the SELIC rate for the period
        logging.info(rate_selic_in_period, 'taxa_selic_no_periodo')
        logging.info(accumulated_in_period, 'accumulated_in_period')
        logging.info(accumulated_interval_filling_rj, 'accumulated_interval_filling_rj')
        return rate_selic_in_period * 100

    def calcule_composto(self):
        filling_date = self.rate_selic.get_rate_by_date(self.filling_date)
        rate_date_rj = self.rate_selic.get_rate_by_date(self.data_rj)
        rate_data_filling_accumulated = filling_date.get_accumulated
        rate_base_date_rj_accumulated = rate_date_rj.get_accumulated
        logging.info(f"rate_data_filling_accumulated: {rate_data_filling_accumulated}")
        logging.info(f"rate_base_date_rj_accumulated: {rate_base_date_rj_accumulated}")
        logging.info(rate_base_date_rj_accumulated / rate_data_filling_accumulated)
        return (rate_base_date_rj_accumulated / rate_data_filling_accumulated)


class ClasseTemplate(AbstractModel):
    classe = models.ForeignKey(Classes, on_delete=models.PROTECT)
    templates = models.ManyToManyField(Template, blank=True)
