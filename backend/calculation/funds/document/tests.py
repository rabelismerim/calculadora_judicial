"""
This module defines a test class for testing the Document API endpoints.

The DocumentTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Document objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods: - test_api_a_post_documents: Sends a POST request to create a new Document object and asserts a successful
response status code - test_api_b_get_documents: Sends a GET request to retrieve a list of Document objects and
asserts a successful response status code and the presence of at least one Document object in the response data

Attributes:
- None
"""
from calculation.funds.document.models import FundDocument
from calculation.models import Calculation
from calculation.tests import CalculationValues
from core.abstract.tests import AbstractTest, generate_name
from creditors.models import Creditor
from creditors.tests import CreditorValues
from rates.models import Rate, Template


def get_create_fund():
    payload = {
        'name': generate_name(),
        'calculation_id': Calculation.objects.first().id,
        'rate_id': Rate.objects.first().id,
        'template_id': Template.objects.first().id,
    }

    fund = FundDocument.objects.first()
    if not fund:
        fund = FundDocument.objects.create(**payload)
    return fund.id


class FundsDocumentTest(AbstractTest):
    """Funds Document related tests"""

    path = f'calculation/funds/documents/{get_create_fund()}'
    calculation_id = None

    def __get_create_creditor(self, physical_person: bool):
        payload = Creditor.objects.filter(physical_person=physical_person).first()
        if payload:
            return payload.id

        payload = CreditorValues().get_creditor(physical_person=physical_person)
        path = 'creditors'
        response = self.post(path, payload)  # creditor
        return response.content['creditor']['id']

    def __get_create_calculation(self, physical_person: bool):
        calculation = Calculation.objects.filter(creditor__physical_person=physical_person, funds__isnull=True,
                                                 fundirrf__isnull=True).first()
        if calculation:
            return calculation.id

        parameters = CalculationValues.calculation
        parameters['creditor_id'] = self.__get_create_creditor(physical_person)
        path = 'calculation'
        response = self.post(path, parameters)
        return response.content['calculation']['id']

    def setUp(self):
        set_up = super().setUp()
        self.calculation_agreement_id = self.__get_create_calculation(True)
        self.calculation_docs_id = self.__get_create_calculation(False)
        return set_up

    @AbstractTest.execute_before_and_after
    def test_api_post_document(self):
        """Assert post statements detail"""

        statements = [
            ({
                 "calculation_id": self.calculation_docs_id,
                 "classes": {
                     "classe": "1"
                 },
                 "coins": {
                     "coin": "B",
                     "value": 500
                 },
                 "archive_json": {},
                 "rate_id": str(Rate.objects.first().id),
                 "template_id": str(Template.objects.first().id),
                 "data_base": "2014-01-02",
                 "historical_value": 1500,
                 "number": generate_name(),
                 "name": generate_name(),
                 "is_extraconcursal": False,
             },
             {'corrected_value': 1520.5231791763986, 'index_data_base': 2.748073182623919,
              'index_recovering': 2.7856726481684837},
             {'total_historical': 1500, 'total_default_interest': 262.03682787806605,
              'total_fine': 17.825600070544645,
              'total_due': 1800.3856071250093,
              'total_days': 517,
              }),
            ({
                 "calculation_id": self.calculation_docs_id,
                 "classes": {
                     "classe": "1"
                 },
                 "coins": {
                     "coin": "B",
                     "value": 500
                 },
                 "archive_json": {},
                 "rate_id": str(Rate.objects.first().id),
                 "template_id": str(Template.objects.first().id),
                 "data_base": "1999-06-09",
                 "historical_value": 500,
                 "number": generate_name(),
                 "name": generate_name(),
                 "is_extraconcursal": False,
             }, {'corrected_value': 658.6255085039053,
                 'index_data_base': 2.114762192020358,
                 'index_recovering': 2.7856726481684837},
             {'total_historical': 500, 'total_default_interest': 1264.560976327498,
              'total_fine': 19.231864848314036,
              'total_due': 1942.4183496797173,
              'total_days': 5760,
              }),
        ]

        for statement, true_monetary_correction, arrears_charges in statements:
            response = self.post('calculation/funds/documents', statement)
            self.assertEqual(response.status_code, 201)
            new_statement = response.content['fund_document']
            fund = new_statement['total']
            monetary_correction = new_statement['statement']['monetary_correction']
            self.assertEqual(fund['total_historical'], arrears_charges['total_historical'])
            self.assertEqual(fund['total_default_interest'], arrears_charges['total_default_interest'])
            self.assertEqual(fund['total_fine'], arrears_charges['total_fine'])
            self.assertEqual(fund['total_due'], arrears_charges['total_due'])
            self.assertEqual(fund['total_days'], arrears_charges['total_days'])

            self.assertEqual(monetary_correction['corrected_value'], true_monetary_correction['corrected_value'])
            self.assertEqual(monetary_correction['index_data_base'], true_monetary_correction['index_data_base'])
            self.assertEqual(monetary_correction['index_recovering'], true_monetary_correction['index_recovering'])
        return statements

    @AbstractTest.execute_before_and_after
    def test_api_a_post_statement_funds_agreement(self):
        """Assert post agreement detail"""
        value = 1500
        data_base = "2014-01-02"
        number = generate_name()
        statement = {
            "calculation_id": self.calculation_agreement_id,
            "classes": {
                "classe": "1"
            },
            "coins": {
                "coin": "B",
                "value": 500
            },
            'fine': 200,
            'has_custom_fine': True,
            "archive_json": {},
            "rate_id": str(Rate.objects.first().id),
            "template_id": str(Template.objects.first().id),
            "name": generate_name(),
            "is_extraconcursal": False,
            "data_base": data_base,
            "historical_value": value,
            "number": number
        }

        response = self.post('calculation/funds/documents', statement)
        self.assertEqual(201, response.status_code)
        new_statement = response.content['fund_document']
        return new_statement
