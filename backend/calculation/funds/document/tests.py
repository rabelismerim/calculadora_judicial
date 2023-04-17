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
from calculation.funds.models import Funds
from calculation.models import Calculation
from core.abstract.tests import AbstractTest, generate_name


class FundsDocumentTest(AbstractTest):
    """Funds Document related tests"""

    @AbstractTest.execute_before_and_after
    def test_api_post_statement_funds_integrations(self):
        """Assert post statements detail"""
        calculation = Calculation.objects.first()
        statements = [
            ({
                 "calculation_id": str(calculation.id),
                 "statement": {
                     "data_base": "2014-01-02",
                     "historical_value": 1500,
                     "number": generate_name()
                 },
                 "name": generate_name()
             },
             {'corrected_value': 1520.5231791763986, 'index_data_base': 2.748073182623919,
              'index_recovering': 2.7856726481684837},
             {'total_historical': 1500, 'total_default_interest': 262.03682787806605,
              'total_fine': 17.825600070544645,
              'total_due': 1800.3856071250093,
              'total_days': 517,
              }),
            ({
                 "calculation_id": str(calculation.id),
                 "statement": {
                     "data_base": "1999-06-09",
                     "historical_value": 500,
                     "number": generate_name()
                 },
                 "name": generate_name()
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
            new_statement = response.content['fund_document']
            fund = new_statement['fund']
            monetary_correction = new_statement['fund']['statement']['monetary_correction']
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
    def test_api_a_post_statement_funds_documents(self):
        """Assert get lawyers detail"""
        calculation = Calculation.objects.first()
        value = 1500
        data_base = "2014-01-02"
        number = generate_name()
        statement = {
            "calculation_id": str(calculation.id),
            "statement": {
                "data_base": data_base,
                "historical_value": value,
                "number": number
            },
            "name": generate_name()
        }

        response = self.post('calculation/funds/documents', statement)
        new_statement = response.content['fund_document']
        return new_statement

    @AbstractTest.execute_before_and_after
    def test_api_b_post_statement_funds(self):
        """Assert get lawyers detail"""
        fund = Funds.objects.first()
        value = 200
        data_base = "2020-03-23"
        dsr_reflexes = 100

        statement_funds = {
            "fund_id": str(fund.id),
            "data_base": data_base,
            "historical_value": value,
            "dsr_reflexes": dsr_reflexes,
            "summary": True
        }

        response = self.post('calculation/funds/labor', statement_funds)
        new_statement = response.content['statement_funds']
        return new_statement

    @AbstractTest.execute_before_and_after
    def test_api_c_post_statement_funds_integrations(self):
        """Assert get lawyers detail"""
        fund = Funds.objects.first()
        value = 559
        data_base = "2007-11-12"
        description = generate_name()

        statement = {
            "fund_id": str(fund.id),
            'description': description,
            "data_base": data_base,
            "historical_value": value,
            "summary": True
        }

        response = self.post('calculation/funds/labor/integrations', statement)
        new_statement = response.content['statement_funds_integrations']
        return new_statement
