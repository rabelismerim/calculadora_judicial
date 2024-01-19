"""
Registers models from the "rates" app to the Django admin site and defines an action to load data from Excel files for the "RateFile" model.

Functions:
- load_files: Action to load data from an Excel file associated with the selected "RateFile" objects and save the data as instances of the "Rate" model.
- CustomRateFile: Custom admin class for the "RateFile" model that includes the "load_files" action.

Modules:
- django.contrib.admin: Django's built-in administration interface.
- django.contrib.messages: Django's messaging framework.
- rates.models: Models for the "rates" app.
- rates.schemas: Schema for validating data from Excel files.
"""

from django.contrib import admin, messages

from apps.schedule.views import SCHEDULER
from rates.commands import AutomaticUpdateRates, SetAccumulated
from rates.models import Accumulated, Period, Rate, RateValues, RateFile, IndiceIRRF, Template, TemplateRate, \
    TemplateField, TemplateMainField, TemplateMainSummaryField, TemplateSummaryField, TemplateMainFieldDefault, \
    TemplateFieldDefault, Source, Unit, ClasseTemplate, TemplateFieldChoices, TemplateMainFieldChoices
from utils import parse_job_id, _

admin.site.register(Accumulated)
admin.site.register(Period)
admin.site.register(Source)
admin.site.register(Unit)
admin.site.register(IndiceIRRF)
admin.site.register(Template)
admin.site.register(TemplateRate)
admin.site.register(TemplateField)
admin.site.register(TemplateSummaryField)
admin.site.register(TemplateFieldDefault)
admin.site.register(TemplateMainFieldDefault)
admin.site.register(TemplateMainSummaryField)
admin.site.register(ClasseTemplate)
admin.site.register(TemplateFieldChoices)
admin.site.register(TemplateMainFieldChoices)


@admin.register(TemplateMainField)
class TemplateMainFieldAdmin(admin.ModelAdmin):
    readonly_fields = ('default',)


def load_files(modeladmin, request, queryset):
    """
    This is a function named load_files that takes three arguments: modeladmin, request, and queryset. The function
    loops through the queryset of RateFile objects, getting the Excel data from each one. If the Excel data is not in
    the correct format, it returns an error message and continues to the next file. If there are no rows in the Excel
    data, it continues to the next file. The function then gets the index_name from the associated Rate object and
    creates a new Rate object if one does not exist already. It then loops through the rows of Excel data,
    creating a new RateValues object for each row and associating it with the appropriate Rate object. If the date of
    the RateValues object already exists in the database, it skips that row. If there is an accumulated or period
    value for the row, the function creates new Accumulated or Period objects and associates them with the RateValues
    object. Finally, the new objects are bulk created using the bulk_create method, and success or warning messages
    are displayed depending on whether any indices were loaded or not. Overall, the function's purpose is to load
    rate index data from Excel files into the Rate and RateValues models in the database.
    """
    for obj in queryset:
        rows = obj.get_excel_to_dict()

        if rows is False:
            messages.error(
                request,
                f'O arquivo {obj.filename} não contêm os campos corretos. Necessário ao menos a coluna mes e indice, '
                f'acumulado e periodo são opcionais')
            continue

        if len(rows) == 0:
            continue

        index_name = obj.rate.index
        new_rate, created = Rate.objects.get_or_create(index=index_name, is_per_day=obj.rate.is_per_day)
        cont = 0

        rates = Rate.objects.filter(index=index_name)
        rate_values_list = []
        accumulated_values_list = []
        period_values_list = []
        for data in rows:
            rate_value = data.pop('rate_value', None)
            accumulated = rate_value.get('accumulated', None)
            period = rate_value.get('period', None)
            date = rate_value.get('date')
            value = rate_value.get('value')

            if rates.filter(ratevalues__date=date).exists():
                continue

            rate_value = RateValues(rate=new_rate, date=date, value=value)
            rate_values_list.append(rate_value)
            cont += 1
            if accumulated is not None:
                accumulated = Accumulated(rate_id=rate_value.id, value=accumulated)
                accumulated_values_list.append(accumulated)
            if period is not None:
                period = Period(rate_id=rate_value.id, value=period)
                period_values_list.append(period)
        RateValues.objects.bulk_create(rate_values_list)
        Accumulated.objects.bulk_create(accumulated_values_list)
        Period.objects.bulk_create(period_values_list)
        if cont > 0:
            messages.success(
                request, f'Carregado {cont} indice(s) do arquivo {obj.filename}')
        else:
            messages.warning(
                request, f'Nenhum indice carregado do arquivo {obj.filename}')


class AdminRateFile(admin.ModelAdmin):
    """
    Model admin class for the RateFile model.

    This model admin class provides additional functionality for the RateFile model in the Django admin interface.
    In this case, it adds a load_files action that loads new rate files into the database.
    """
    actions = [load_files]


def scheduler_rates(modeladmin, request, queryset):
    """
    Schedule rate updates for selected Rate objects.

    This method schedules rate updates for the selected Rate objects by creating a new AutomaticUpdateRates object
    for each object and setting up a job with the corresponding periodicity. If the rate is set to be updated daily,
    it uses the every_day() method of the Scheduler. Otherwise, if it's set to be updated monthly, it uses the
    every_day_in_month() method. Finally, it sets the is_active flag to True for each selected Rate object.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    for obj in queryset:
        auto = AutomaticUpdateRates(obj.id).update_rate
        job_id = parse_job_id(obj.index)

        if obj.periodicity == 'D':
            job = SCHEDULER.every_day(job_id, auto)  # OK
        else:
            job = SCHEDULER.every_day_in_month(job_id, auto)  # OK

        if job:
            messages.success(
                request,
                _('The rate {} has been successfully scheduled. Next run at {}').format(obj.index, job.next_run_time))
        else:
            messages.warning(request, _('it was not possible to schedule the index {}').format(obj.index))
        obj.is_active = True
        obj.save()


def resume_scheduler_rates(modeladmin, request, queryset):
    """
    Resume scheduled rate updates for selected Rate objects.

    This method resumes the scheduled rate updates for the selected Rate objects by getting the job_id from the index
    attribute of the object and calling the Scheduler.resume_job() method.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    for obj in queryset:
        job_id = parse_job_id(obj.index)
        job = SCHEDULER.resume_job(job_id)
        messages.success(
            request,
            _('The rate {} has been successfully scheduled. Next run at {}').format(obj.index, job.next_run_time))


def set_accumulated_rates(modeladmin, request, queryset):
    """
    Custom admin action to set accumulated rates for selected objects.

    Args:
        modeladmin: The ModelAdmin instance.
        request: The HTTP request.
        queryset: A QuerySet containing the selected objects.

    This function iterates through the selected objects in the `queryset` and sets the accumulated and period rates
    using the SetAccumulated class.

    Example usage in the admin panel:

    1. Select one or more objects in the admin panel.
    2. Choose the "Set Accumulated Rates" action from the action dropdown.
    3. Click "Go" to apply the action, which will call this function for the selected objects.
    """
    for obj in queryset:
        SetAccumulated(rate_id=obj.id).update_rate()


def update_rates(modeladmin, request, queryset):
    """
    Custom admin action to update missing index dates for selected rates objects.

    Args:
        modeladmin: The ModelAdmin instance.
        request: The HTTP request.
        queryset: A QuerySet containing the selected objects.

    This function iterates through the selected objects in the `queryset` and sets the missing index dates
    using the AutomaticUpdateRates class.

    Example usage in the admin panel:

    1. Select one or more objects in the admin panel.
    2. Choose the "Set Accumulated Rates" action from the action dropdown.
    3. Click "Go" to apply the action, which will call this function for the selected objects.
    """
    for obj in queryset:
        AutomaticUpdateRates(rate_id=obj.id).update_rate()


def force_update_rates(modeladmin, request, queryset):
    """
    Custom admin action to update all available dates for selected rates objects.

    Args:
        modeladmin: The ModelAdmin instance.
        request: The HTTP request.
        queryset: A QuerySet containing the selected objects.

    This function iterates through the selected objects in the `queryset` and sets all available dates
    using the AutomaticUpdateRates class.

    Example usage in the admin panel:

    1. Select one or more objects in the admin panel.
    2. Choose the "Set Accumulated Rates" action from the action dropdown.
    3. Click "Go" to apply the action, which will call this function for the selected objects.
    """
    for obj in queryset:
        AutomaticUpdateRates(rate_id=obj.id, force=True).update_rate()


def pause_scheduler_rates(modeladmin, request, queryset):
    """
    Pause scheduled rate updates for selected Rate objects.

    This method pauses the scheduled rate updates for the selected Rate objects by getting the job_id from the index
    attribute of the object and calling the Scheduler.pause_job() method.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    for obj in queryset:
        job_id = parse_job_id(obj.index)
        job = SCHEDULER.pause_job(job_id)
        if job:
            if job.next_run_time:
                messages.warning(request, _('it was not possible to pause the index {}').format(obj.index))
            else:
                messages.warning(request, _('Index {} was paused successfully').format(obj.index))
        else:
            messages.error(request, _('The scheduler to Index {} was not found').format(obj.index))


def remove_scheduler_rates(modeladmin, request, queryset):
    """
    Remove scheduled rate updates for selected Rate objects.

    This method removes the scheduled rate updates for the selected Rate objects by getting the job_id from the index
    attribute of the object and calling the Scheduler.remove_job() method.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    for obj in queryset:
        job_id = parse_job_id(obj.index)
        SCHEDULER.remove_job(job_id)
        job = SCHEDULER.get_job(job_id)
        if job:
            messages.warning(request, _('it was not possible to delete the index {}').format(obj.index))
        else:
            messages.error(request, _('Index {} was scheduler deleted successfully').format(obj.index))


def inactive_rates(modeladmin, request, queryset):
    """
    Mark selected Rate objects as inactive.

    This method sets the is_active flag to False for the selected Rate objects.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    queryset.update(is_active=False)


def active_rates(modeladmin, request, queryset):
    """
    Mark selected Rate objects as active.

    This method sets the is_active flag to True for the selected Rate objects.

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    queryset.update(is_active=True)


def delete_rate_values(modeladmin, request, queryset):
    """
    Remove all rate values associate a rate

    Args:
        modeladmin: The model admin instance.
        request: The request object.
        queryset: A queryset containing the selected Rate objects.
    """
    for rate in queryset:
        rate.ratevalues_set.all().delete()


class AdminRate(admin.ModelAdmin):
    """
    Model admin class for the Rate model.

    This model admin class provides additional functionality for the Rate model in the Django admin interface. In
    this case, it adds several actions that allow scheduling, resuming, pausing, and removing rate update jobs for
    selected Rate objects. It also provides search fields and list display options for easy browsing of rates.
    """
    actions = [scheduler_rates, resume_scheduler_rates, pause_scheduler_rates, remove_scheduler_rates, inactive_rates,
               active_rates, set_accumulated_rates, update_rates, force_update_rates, delete_rate_values]
    search_fields = ('date', 'index', 'value')
    list_display = (
        'code', 'scheduler_status', 'scheduler_description', 'get_periodicity_display', 'is_active',
        'total_rate_values', 'initial_accumulated')
    readonly_fields = ('unit', 'source', 'total_rate_values')


class AdminRateValues(admin.ModelAdmin):
    search_fields = ('date',)


admin.site.register(Rate, AdminRate)
admin.site.register(RateFile, AdminRateFile)
admin.site.register(RateValues, AdminRateValues)
