from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand
from django.db import OperationalError
from django_apscheduler.jobstores import DjangoJobStore
from config import settings

from datetime import datetime, time

from utils import _


class SchedulerCommand(BaseCommand):
    """
    A class to create and manage scheduled jobs using BackgroundScheduler from the apscheduler library.

    Attributes:
        scheduler (BackgroundScheduler): a scheduler instance with DjangoJobStore job store.
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.start()

    def __handle(self, schedule_type, job_id, func, at_time, days='*', day_of_week='*', day_of_month='*', months='*'):
        """
            A private method to handle adding jobs to the scheduler based on different schedule types.

            Args:
                schedule_type (str): the type of schedule. Valid values are 'date', 'day', 'week', 'month', and 'months'.
                job_id (str): the ID of the job.
                func (callable): the function or callable object to execute when the job is triggered.
                at_time (datetime): the date and time to start the job.
                days (str): a string representation of days of the month, separated by commas. Default is '*'.
                day_of_week (str): a string representation of days of the week, separated by commas. Default is '*'.
                day_of_month (str): a string representation of days of the month, separated by commas. Default is '*'.
                months (str): a string representation of months of the year, separated by commas. Default is '*'.

            Returns:
                None.

            Raises:
                ValueError: if the schedule_type argument passed is not valid.

            Examples:
                scheduler_command = SchedulerCommand()

                To schedule a job to run once at 2022-01-01 00:00:00:
                scheduler_command.at('job_id_1', my_func, datetime(2022, 1, 1, 0, 0, 0))

                To schedule a job to run every day at 12:30:
                scheduler_command.every_day('job_id_2', my_func, at_time=time(hour=12, minute=30))

                To schedule a job to run every Tuesday and Friday at 5:00:
                scheduler_command.every_week('job_id_3', my_func, day_of_week='2,5', at_time=time(hour=5, minute=0))

                To schedule a job to run on the 15th day of each month at 8:30:
                scheduler_command.every_day_in_month('job_id_4', my_func, day_of_month='15', at_time=time(hour=8, minute=30))

                To schedule a job to run on the 1st day of every 3 months at 7:00:
                scheduler_command.every_month('job_id_5', my_func, day_of_month='1', months='*/3', at_time=time(hour=7, minute=0))
            """
        if callable(func) is False:
            raise ValueError(_('Argument func is necessary a callable'))
        if not at_time:
            at_time = time(hour=0, minute=0)
        hour, minute, second = at_time.hour, at_time.minute, at_time.second
        if schedule_type == 'day':
            payload = {'day': days, 'hour': hour, 'minute': minute, 'second': second}
        elif schedule_type == 'week':
            payload = {'day_of_week': day_of_week, 'hour': hour, 'minute': minute, 'second': second}
        elif schedule_type == 'month':
            payload = {'day': day_of_month, 'hour': hour, 'minute': minute, 'second': second}
        elif schedule_type == 'months':
            payload = {'day': day_of_month, 'month': months, 'hour': hour, 'minute': minute, 'second': second}
        else:
            payload = {'hour': at_time.hour, 'minute': at_time.minute, 'day': at_time.day, 'month': at_time.month,
                       'second': at_time.second, 'year': at_time.year}
        try:
            self.scheduler.add_job(func, executor='default', trigger=CronTrigger(**payload), id=job_id, job_id=job_id,
                                   replace_existing=True)
        except OperationalError:
            pass

    def at(self, job_id, func, at_time: datetime):
        """
        Add a one-time job at a specific date and time.

        Args:
            job_id (str): the ID of the job.
            func (callable): the function or callable object to execute when the job is triggered.
            at_time (datetime): the date and time to start the job.

        Examples:
            from datetime import datetime
            scheduler_command = SchedulerCommand()

            To schedule a job to run once at 2022-01-01 00:00:00:
            scheduler_command.every_day('job_id_2', my_func, at_time=datetime(2022, 1, 1, 0, 0, 0))
        """
        self.__handle('date', job_id, func, at_time=at_time)

    def every_day(self, job_id, func, days='*', at_time=None):
        """
        Add a single job for all days, or specific days.

        Args:
            job_id (str): the ID of the job.
            func (callable): the function or callable object to execute when the job is triggered.
            days (str): a string representation of days of the month, separated by commas. Default is '*'.
            at_time (datetime): the date and time to start the job.

        Examples:
            scheduler_command = SchedulerCommand()

            To schedule a job to run every day:
            scheduler_command.every_day('job_id_2', my_func)

            To schedule a job to run in days 12 and 14, at 12:30:
            scheduler_command.every_day('job_id_2', my_func, days='12,14', at_time=time(hour=12, minute=30))
        """
        self.__handle('day', job_id, func, days=days, at_time=at_time)

    def every_week(self, job_id, func, day_of_week='*', at_time=None):
        """
        Add a job to run every week on specific days and time.

        Args:
            job_id (str): the ID of the job.
            func (callable): the function or callable object to execute when the job is triggered.
            day_of_week (str): a string representation of days of the week, separated by commas. Default is '*'.
            at_time (datetime.time): the time of day to start the job. Default is midnight.

        Examples:
            scheduler_command = SchedulerCommand()

            To schedule a job to run every day of week:
            scheduler_command.every_week('job_id_3', my_func)

            To schedule a job to run every Tuesday and Friday at 5:00:
            scheduler_command.every_week('job_id_3', my_func, day_of_week='2,5', at_time=time(hour=5, minute=0))
        """
        self.__handle('week', job_id, func, day_of_week=str(day_of_week), at_time=at_time)

    def every_day_in_month(self, job_id, func, day_of_month='1', at_time=None):
        """
        Add a job to run every month on specific day and time.

        Args:
            job_id (str): the ID of the job.
            func (callable): the function or callable object to execute when the job is triggered.
            day_of_month (str): a string representation of days of the month, separated by commas. Default is '1'.
            at_time (datetime.time): the time of day to start the job. Default is midnight.

        Examples:
            scheduler_command = SchedulerCommand()

            To schedule a job to run every month:
            scheduler_command.every_day_in_month('job_id_4', my_func)

            To schedule a job to run on the 15th day of each month at 8:30:
            scheduler_command.every_day_in_month('job_id_4', my_func, day_of_month='15', at_time=time(hour=8, minute=30))
        """
        self.__handle('month', job_id, func, day_of_month=day_of_month, at_time=at_time)

    def every_month(self, job_id, func, day_of_month='1', months='*', at_time=None):
        """
        Add a job to run in all or certain months, being able to specify the day and time

        Args:
            job_id (str): the ID of the job.
            func (callable): the function or callable object to execute when the job is triggered.
            day_of_month (str): a string representation of days of the month, separated by commas. Default is '1'.
            months (str): a string representation of months in year, separated by commas. Default is '*'.
            at_time (datetime.time): the time of day to start the job. Default is midnight.

        Examples:
            scheduler_command = SchedulerCommand()

            To schedule a job to run every month:
            scheduler_command.every_month('job_id_5', my_func, day_of_month='1')

            To schedule a job to run on the 1st day of every 1th month at 7:00:
            scheduler_command.every_month('job_id_5', my_func, day_of_month='1', months='1', at_time=time(hour=7, minute=0))

            To schedule a task to run on the 15th of the 7th and 8th month:
            scheduler_command.every_day_in_month('job_id_4', my_func, day_of_month='15', months='7, 8')
        """
        self.__handle('months', job_id, func, day_of_month=day_of_month, months=months, at_time=at_time)

    def remove_job(self, job_id):
        """Removes a specific job by ending its execution schedule"""
        try:
            self.scheduler.remove_job(str(job_id))
        except JobLookupError:
            pass


SCHEDULER = SchedulerCommand()
