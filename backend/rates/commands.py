import datetime
import csv
import decimal
import json
import time

import requests
from dateutil import parser
from django.db.models import Avg, F
from requests import JSONDecodeError
from decimal import Decimal
from unidecode import unidecode

from rates.models import Rate, RateValues, Period, Accumulated


class Date:
    """
    A class for parsing and normalizing date strings into a standardized format.

    :param date_str: A string containing a date in either "YYYY-MM-DD" or "DD/MM/YYYY" format, or the string "today".
    """

    def __init__(self, date_str):
        """
        Initializes an object with a date string in either "YYYY-MM-DD" or "DD/MM/YYYY" format,
        or replaces it with the current date if the string is "today".

        :param date_str: The date string to parse and normalize.
        """
        if not date_str:
            self.date = None
        else:
            date_str = str(date_str)
            if date_str == 'today':
                date_str = str(datetime.datetime.now().date())
            try:
                date_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')

            self.date = date_obj.strftime('%d/%m/%Y')


class BCB:
    """Class for accessing data from Brazil's Central Bank (BCB) API."""
    __base_url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados'

    @staticmethod
    def _get_payload(start_date, end_date):
        """
        Returns a dictionary with the payload data for a given date range.

        :param start_date: The start date of the range in string format "YYYY-MM-DD" or "today" (default).
        :param end_date: The end date of the range in string format "YYYY-MM-DD" or "today" (default).
        :return: A dictionary with the payload data.
        """
        start_date = Date(start_date).date
        finish_date = Date(end_date).date
        payload = {'formato': 'json'}

        if start_date:
            payload['dataInicial'] = start_date
        if finish_date:
            payload['dataFinal'] = finish_date
        return payload

    def get(self, code, start='today', end='today'):
        """
        Retrieves data from the BCB API for the given series code and date range.

        :param code: The code for the series to retrieve.
        :param start: The start date of the range in string format "YYYY-MM-DD" or "today" (default).
        :param end: The end date of the range in string format "YYYY-MM-DD" or "today" (default).
        :return: A JSON object with the retrieved data.
        :raises Exception: If the request returns an error status.
        """

        if not code or int(code) < 1:
            print('Código do Bacen não informado')
        payload = self._get_payload(start, end)
        res = requests.get(self.__base_url.format(code), params=payload)
        if res.status_code != 200:
            raise Exception('Download error: code = {}'.format(code))
        try:
            return self._parse_data_response(res.json())
        except JSONDecodeError:
            return []

    def _parse_data_response(self, data: list) -> list:
        """
        Parse a list of rate data dictionaries to a new list with date and value fields.

        This method takes a list of rate data dictionaries and converts each dictionary into a new dictionary with date and value keys.
        The date string is parsed into a date object and reformatted to match the "YYYY-MM-DD" format.

        Args:
            data (list): A list of rate data dictionaries, where each dictionary contains a "data" and "valor" key.

        :return:
            list: A new list of dictionaries where each dictionary contains a "date" and "value" key.
        """
        new_data = []
        for x in data:
            new_data.append({'date': datetime.datetime.strptime(x['data'], '%d/%m/%Y').date(), 'value': x['valor']})
        return new_data

    def _parse_data(self, date):
        """Parse a date string into the "YYYY-MM-DD" format.

        This method parses a date string into the "YYYY-MM-DD" format expected by the program.
        If the date cannot be parsed, it returns None.

        Args:
            date (str): A date string to parse.

        :return:
            str or None: The parsed date in "YYYY-MM-DD" format, or None if it could not be parsed.
        """
        if '&ordm' in date:
            date = date.split('.')[-1]
        try:
            date = str(parser.parse(date, default=datetime.datetime(1900, 1, 1)).date())
        except ValueError:
            month_dict = {
                'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
                'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                'set': '09', 'out': 10, 'nov': 11, 'dez': 12
            }
            try:
                month, year = date.split("/")
                date = str(
                    datetime.datetime.strptime(f'01/{month_dict.get(month)}/{year}', '%d/%m/%Y'))
            except ValueError:
                date = None
        return date

    def _parse_row(self, row):
        """
        Parses a row of data from the input CSV file and converts it into a dictionary object with normalized keys.

        :param row: The row of data as a dictionary.
        :return: A dictionary object with the normalized keys and their corresponding values.
        """
        list_values = list(row.values()).copy()
        obj = row.copy()
        if isinstance(list_values[-1], list):
            list_end = list_values.pop(len(list_values) - 1)
            list_values.extend(list_end)
        for cont, values in enumerate(list_values):
            if isinstance(values, list):
                values = ' '.upper().join(values)
            if values.strip() in ['D', 'M', 'A', 'Q', 'T'] and len(values.strip()) == 1:
                obj = {'Código': list_values[0],
                       ' Nome completo': ' '.join(list_values[1: cont - 2]),
                       ' Unidade': list_values[cont - 1],
                       ' Periodicidade': values.strip(),
                       ' Data início': list_values[len(list_values) - 4],
                       ' Data do último valor da série': list_values[len(list_values) - 3],
                       ' Fonte': list_values[len(list_values) - 2],
                       ' Especial': list_values[len(list_values) - 1]}
                break
        return obj

    def parse_csv(self):
        """
        Reads and parses data from an input CSV file containing series information from the BCB API,
        converts it into a list of dictionaries with normalized keys, and writes it to an output JSON file.

        :return: A list of dictionary objects with normalized keys and their corresponding values.
        """
        input_file = 'lciSeriesCsv.jsp'
        output_file = 'rates.json'

        data = []

        with open(input_file) as f:
            reader = csv.DictReader(f)

            for row in reader:
                normalized_row = {}
                if None in row.keys():
                    obj = self._parse_row(row)
                else:
                    obj = row.copy()

                for header, value in obj.items():
                    if not header:
                        continue
                    header = unidecode(header.strip()).replace(' ', '_').lower()

                    if isinstance(value, list):
                        value = ' '.join(value)
                    value = ' '.join(value.strip().split())

                    if header in ['data_do_ultimo_valor_da_serie', 'data_inicio']:
                        value = self._parse_data(value)

                    elif header == 'unidade' and value.startswith("% a."):
                        value = value.replace("% ", '', 1).strip()

                    if isinstance(value, str):
                        value = ' '.join(value.strip().split())
                    normalized_row[header] = value

                data.append(normalized_row)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data


class AutomaticUpdateRates:
    """
    Class for handling automatic rate updates.

    This class provides a mechanism for updating rates automatically at regular intervals.
    It contains an update_rate() method that fetches the latest rates from the BCB API and adds them to the database if they don't already exist.

    Attributes:
        rate_id (int): The id of the Rate object to be updated.
    """

    def __init__(self, rate_id, force=False):
        self.rate_id = rate_id
        self.force = force

    def update_rate(self):
        """
        Update the associated Rate object with the latest values from the BCB API.

        This method fetches the latest rate values from the BCB API and adds them to the associated Rate object.
        It uses the get_last_date() method to determine the date of the most recent rate value and fetches data from
        that date onwards.
        If there are any new rate values, they are added to the database using the bulk_create() method.
        Finally, it updates the last_update field of the Rate object and saves it to the database.
        """
        rate = Rate.objects.filter(id=self.rate_id).first()
        if self.force:
            last_rate = None
        else:
            last_rate = rate.get_last_date()
        bcb = BCB()
        codes = bcb.get(rate.code, start=last_rate)
        rate_values_bulk = []
        rate_values = rate.ratevalues_set.all()
        rate_values_ids = rate_values.values_list('id', flat=True)
        Period.objects.filter(rate__id__in=rate_values_ids).delete()
        Accumulated.objects.filter(rate__id__in=rate_values_ids).delete()
        rate.ratevalues_set.all().delete()
        rate_values = rate.ratevalues_set.all()

        for code in codes:
            if not rate_values.filter(date=code['date']).exists():
                new_rate_values = RateValues(rate=rate, date=code['date'], value=code['value'])
                rate_values_bulk.append(new_rate_values)
        RateValues.objects.bulk_create(rate_values_bulk)
        rate.last_update = datetime.datetime.now()
        rate.save()
        SetAccumulated(rate_id=rate.id).update_rate()
        with open(f'{rate.code}_code.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(codes, default=str))


class SetAccumulated:
    """
    Class for handling automatic rate updates.

    This class provides a mechanism for updating rates automatically at regular intervals.
    It contains an update_rate() method that fetches the latest rates from the BCB API and adds them to the database if they don't already exist.

    Attributes:
        rate_id (int): The id of the Rate object to be updated.
    """

    def __init__(self, rate_id):
        self.rate_id = rate_id

    def update_rate(self):
        """
        Update the associated Rate object with the latest values from the BCB API.

        This method fetches the latest rate values from the BCB API and adds them to the associated Rate object.
        It uses the get_last_date() method to determine the date of the most recent rate value and fetches data from
        that date onwards.
        If there are any new rate values, they are added to the database using the bulk_create() method.
        Finally, it updates the last_update field of the Rate object and saves it to the database.
        """

        rate = Rate.objects.filter(id=self.rate_id).first()
        rate_values = rate.ratevalues_set.all().order_by('date')
        accumulated = rate.initial_accumulated

        if accumulated is None:
            return

        first_rate = rate_values.first()
        if not first_rate:
            print('Rate values não cadastrado')
            return

        period = 1 + first_rate.value / 100

        Accumulated.objects.update_or_create(rate=first_rate, defaults={'value': accumulated})
        Period.objects.update_or_create(rate=first_rate, defaults={'value': period})

        for rate_value in rate_values[1:]:
            value = rate_value.value
            period = 1 + value / 100

            accumulated = period * accumulated
            Accumulated.objects.update_or_create(rate=rate_value, defaults={'value': accumulated})
            Period.objects.update_or_create(rate=rate_value, defaults={'value': period})

        self.update_average()

    def update_average(self):
        """
        Update the average values of a Rate instance.

        This method calculates and updates the average values for a Rate instance. It first retrieves the Rate
        object based on the provided `rate_id`, and then calculates the average values for the specified time period.

        The algorithm follows these steps:
        1. Retrieve the Rate object based on `rate_id`.
        2. Delete all existing rate values associated with the Rate instance.
        3. Retrieve the initial accumulated value from the Rate object.
        4. If there's no initial accumulated value, the method returns without updating.
        5. Get a list of media rates associated with the Rate.
        6. If there are fewer than 2 media rates, the method returns without updating.
        7. Retrieve rate values for the specified time period from the media rates.
        8. Calculate average values and periods for these rate values.
        9. Create or update the first rate value with the calculated average value and accumulated value.
        10. Update the associated accumulated and period values for the first rate value.
        11. Loop through the remaining rate values, updating them with average values and updating accumulated and
        period values.

        This method is designed to maintain the average values for a Rate object based on its related media rates.

        Note: Make sure to pass the `rate_id` when calling this method to update the correct Rate object.
        """

        rate = Rate.objects.filter(id=self.rate_id).first()
        accumulated = rate.initial_accumulated

        if not accumulated:
            return

        media_rates_ids = rate.average.all().values_list('id', flat=True)

        if len(media_rates_ids) < 2:
            return

        rate.ratevalues_set.all().delete()

        rate_values = RateValues.objects.filter(rate__id__in=media_rates_ids, date__gte=rate.start_indice)
        rate_values_with_average = rate_values.values('date').order_by('date').annotate(
            average_period=Avg(F('period__value')), average_value=Avg(F('value'))).filter(average_period__isnull=False)

        first_rate = rate_values_with_average.first()
        first_rate_average_value = first_rate['average_value']
        first_rate_average_period = first_rate['average_period']

        new_rate_value, created = RateValues.objects.update_or_create(rate=rate, date=first_rate["date"],
                                                                      defaults={'value': first_rate_average_value})
        Accumulated.objects.update_or_create(rate=new_rate_value, defaults={'value': accumulated})
        Period.objects.update_or_create(rate=new_rate_value, defaults={'value': first_rate_average_period})

        for rate_value in rate_values_with_average[1:]:
            average_value = rate_value["average_value"]
            average_period = rate_value["average_period"]
            rate_date = rate_value["date"]
            accumulated = average_period * accumulated

            new_rate_value, created = RateValues.objects.update_or_create(rate=rate, date=rate_date,
                                                                          defaults={'value': average_value})
            Accumulated.objects.update_or_create(rate=new_rate_value, defaults={'value': accumulated})
            Period.objects.update_or_create(rate=new_rate_value, defaults={'value': average_period})
