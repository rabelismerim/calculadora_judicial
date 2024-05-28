import logging

from django.db import transaction, IntegrityError
from django.utils.timezone import now

from dashboard.models import LoginRecord


class LoginMiddleware:
    """
    A middleware class that creates a login record for the user, if one does not exist for the current date.

    Args:
        get_response: A callable object that represents the next middleware or view in the process.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Creates a login record for the user, if one does not exist for the current date.

        Args:
            request: An object that contains information about the current request.

        :return:
            response: The response object from the next middleware or view in the process.
        """
        response = self.get_response(request)
        user = request.user

        if user.is_authenticated:
            today = now().date()
            login_date = user.login_date

            if not login_date or login_date != today:
                record_exists_today = LoginRecord.objects.filter(user=user, login_date=today).exists()

                if not record_exists_today:
                    try:
                        LoginRecord.objects.create(user=user)
                    except IntegrityError as e:
                        logging.error(e)
                user.login_date = today
                user.save()
        return response
