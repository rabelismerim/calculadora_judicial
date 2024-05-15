"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import datetime as dt
from calendar import monthrange
from datetime import datetime, timedelta, time, date
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import serializers

from calculation.models import Calculation
from core.abstract.models import AbstractModel
from projects.models import Project
from utils import get_user_model, _

User = get_user_model()

QUERY_DASHBOARD = [
    {
        "name": "dashboard_start_day_date",
        "field": "dashboard_start_day_date",
        "in": "query",
        "required": False,
        "description": str(_("Start day date")),
        "schema": {"type": "date"}
    },
    {
        "name": "dashboard_end_day_date",
        "field": "dashboard_end_day_date",
        "in": "query",
        "required": False,
        "description": str(_("End day date")),
        "schema": {"type": "date"}
    },
    {
        "name": "dashboard_start_month_date",
        "field": "dashboard_start_month_date",
        "in": "query",
        "required": False,
        "description": str(_("Start month date")),
        "schema": {"type": "date"}
    },
    {
        "name": "dashboard_end_month_date",
        "field": "dashboard_end_month_date",
        "in": "query",
        "required": False,
        "description": str(_("End month date")),
        "schema": {"type": "date"}
    },
]


class Query:

    @staticmethod
    def __parse_date(date_string):
        """Parse string to date"""
        return dt.datetime.strptime(date_string, '%Y-%m-%d').date()

    @staticmethod
    def __parse_datetime(date_string):
        """Parse string to datetime"""
        return dt.datetime.strptime(date_string, '%Y-%m-%d %H:%M')

    @staticmethod
    def __parse_bool(text):
        """Parse string to bool"""
        return str(text).lower() in 'true'

    def __get_type_by_instance(self, instance):
        """Get instance, type, parser and legend by field schema type"""
        types = {
            'string': {'type': str, 'parser': str, 'legend': 'string'},
            'date': {'type': dt.date, 'parser': self.__parse_date, 'legend': '2001-12-30'},
            'datetime': {'type': dt.date, 'parser': self.__parse_datetime, 'legend': '2001-12-30 23:01'},
            'float': {'type': float, 'parser': float, 'legend': '01.00'},
            'int': {'type': int, 'parser': int, 'legend': '1'},
            'bool': {'type': bool, 'parser': self.__parse_bool, 'legend': 'True/False'},
        }

        return types.get(instance, str)

    def get_query(self, request):
        """Validate parameters received in query params, returning query values"""
        query = {}

        for valid_params in self.query_params:
            type_instance = valid_params['schema']['type']
            field = valid_params['field']
            name = valid_params['name']
            value = request.query_params.get(name)
            if value:
                instance = self.__get_type_by_instance(type_instance)
                try:
                    value = instance['parser'](value)
                except (ValueError, KeyError):
                    pass
                if isinstance(value, instance['type']):
                    query[field] = value
                else:
                    raise serializers.ValidationError(
                        {name: _('Field in invalid format. It must be in the format {}').format(instance["legend"])})
        return query


class Dashboard(AbstractModel, Query):
    """
    A class that implements a dashboard with various methods to get information and calculations from the database.

    Attributes:
        query_params (str): A string that contains a query used to get information from the database.

    Methods:
        calc_by_phase(request, *args, **kwargs):
            Gets calculations for a given user and returns the number of calculations by phase.

        range_for_days(request):
            Gets login records for a given time period (up to 7 days) and returns the number of login records per day.

        range_for_month(request):
            Gets login records for a given time period (up to 12 months) and returns the number of login records per month.
    """
    query_params = QUERY_DASHBOARD

    def has_permission(self, request):
        perms = ['can_view_all_projects']
        return request.user.has_permission(perms)

    def calc_by_phase(self, request):
        if self.has_permission(request):
            calculations = Calculation.objects.all().values_list('id', flat=True).distinct()
        else:
            calculations = Calculation.objects.filter(
                creditor__recovering__project__engagement__users__user=request.user).values_list('id',
                                                                                                 flat=True).distinct()
        total = calculations.count()
        total_adm = calculations.filter(is_adm=True).distinct().count()
        total_judicial = total - total_adm
        return {
            'adm': total_adm,
            'judicial': total_judicial,

        }

    def range_for_days(self, request):
        """
        Gets login records for a given time period (up to 7 days) and returns the number of login records per day.

        Args:
            request: An object that contains information about the current request.

        :return:
            list: A list of dictionaries. Each dictionary contains the number of login records per day for a given time period.
        """
        query = self.get_query(request)
        end_date = query.get('dashboard_end_day_date') or datetime.today().date()
        start_date = query.get('dashboard_start_day_date') or end_date - timedelta(days=6)
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)
        end_date = min(end_date, datetime.today())
        datas = [start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)]

        registros_by_range_days = LoginRecord.objects.filter(login_date__range=(start_date.date(), end_date.date()),
                                                             login_date__isnull=False) \
            .order_by('login_date')

        registros_por_dia_list = []
        for dia in datas:
            dia_formatado = dia.strftime('%Y-%m-%d')
            total_registros = registros_by_range_days.filter(login_date=dia).count()
            registros_por_dia_list.append({'day': dia_formatado, 'total': total_registros})
        return registros_por_dia_list

    def range_for_month(self, request):
        """
        Gets login records for a given time period (up to 12 months) and returns the number of login records per month.

        Args:
            request: An object that contains information about the current request.

        :return:
            list: A list of dictionaries. Each dictionary contains the number of login records per month for a given time period.
        """
        query = self.get_query(request)
        end_date = query.get('dashboard_end_month_date') or date.today()
        start_date = query.get('dashboard_start_month_date') or (end_date - relativedelta(months=11)).replace(day=1)
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)
        end_date = min(end_date, datetime.today())

        start_month = datetime(start_date.year, start_date.month, 1, 0, 0, 0, 0)
        end_month = datetime(end_date.year, end_date.month, 1, 23, 59, 59, 999999) + timedelta(days=31)
        end_month -= timedelta(days=end_month.day)
        end_month = min(end_month, datetime.today())
        months = []
        month = date(start_month.year, start_month.month, 1)
        while month <= end_month.date():
            months.append(month)
            next_month = date(month.year, month.month, 1).replace(month=(month.month % 12) + 1,
                                                                  year=month.year + (month.month // 12))
            month = next_month
        records_by_month_list = []
        for month in months:
            start_month = datetime(month.year, month.month, 1, 0, 0, 0, 0)
            end_month = datetime(month.year, month.month, monthrange(month.year, month.month)[1], 23, 59, 59, 999999)
            end_month = min(end_month, datetime.today())

            records_by_month = LoginRecord.objects.filter(login_date__range=(start_month.date(), end_month.date())) \
                .order_by('login_date')

            month_str = "{}-{:02}".format(month.year, month.month)
            total_registros = records_by_month.filter(login_date__month=month.month).count()
            records_by_month_list.append({'month': month_str, 'total': total_registros})
        return records_by_month_list

    def project_status(self, request):
        projects = Project.objects.all().select_related('legal_manager', 'calculation_manager',
                                                        'financial_manager', 'legal_partner',
                                                        'financial_partner')
        count_status = projects.values('status').annotate(total=Count('id'))

        count_status = list(count_status.values('status', 'total'))

        project_users = projects.values_list('legal_manager__username', 'calculation_manager__username',
                                             'financial_manager__username', 'legal_partner__username',
                                             'financial_partner__username')
        project_users = list(set(chain.from_iterable(project_users)))

        count_users = []

        users = User.objects.all()
        for username in project_users:

            print(type(username), 'user type')
            total = 0

            for project in projects:

                any_user = [
                    str(project.legal_manager) == username,
                    str(project.calculation_manager) == username,
                    str(project.financial_manager) == username,
                    str(project.legal_partner) == username,
                    str(project.financial_partner) == username,
                ]

                if any(any_user):
                    total += 1

            user = users.filter(username=username).first()
            count_users.append({'username': user.get_full_name, 'total': total})

        return {'count_status': count_status, 'count_users': count_users}


class LoginRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField(auto_now_add=True)
    login_tm = models.TimeField()

    def save(self, *args, **kwargs):
        if not self.login_tm:  # Verifica se é uma inserção (não atualização)
            self.login_tm = timezone.localtime().time()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Login Register"
        unique_together = [['user', 'login_date']]

    def __str__(self):
        return f"{self.user.username} {self.login_date}:{self.login_tm}"
