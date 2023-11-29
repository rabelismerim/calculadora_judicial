from django.core.management.base import BaseCommand
from rates.models import Rate, CalculeRate


class Command(BaseCommand):
    """
    A management command to calculate a composite interest rate (SELIC) within a specified period.
    """

    help = 'A management command to calculate a composite interest rate (SELIC) within a specified period.'

    def handle(self, *args, **options):
        """
        Handles a specific process involving SELIC rates within a given period.

        Args:
        *args: Variable length argument list.
        **options: Keyword arguments.

        This function performs calculations to determine the SELIC rate within a specified period
        between two dates using Rate objects.

        The process involves the following steps:
        1. Fetching a Rate object with a specific code from the database.
        2. Defining two dates as string representations ('YYYY-MM-DD') for calculation purposes.
        3. Converting the string dates to datetime objects.
        4. Obtaining the accumulated rate for a specific date from the Rate object.
        5. Calculating the accumulated rate between a specific date and the end of its respective month.
        7. Finalizing the SELIC rate for the period by combining the computed rates.

        Example Usage:
        This function can be called to calculate the SELIC rate within a specific period.
        """
        filling_date = '2016-05-10'
        data_rj = '2019-03-22'
        selic = Rate.objects.filter(code=4390).first()
        accumulated = CalculeRate(filling_date=filling_date, data_rj=data_rj, rate_selic=selic).calcule()
        print(accumulated)
