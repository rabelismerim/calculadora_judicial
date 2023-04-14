"""
This module defines a test class for testing the Funds API endpoints.

The FundsTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Funds objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods: - test_api_a_post_fundss: Sends a POST request to create a new Funds object and asserts a successful
response status code - test_api_b_get_fundss: Sends a GET request to retrieve a list of Funds objects and asserts a
successful response status code and the presence of at least one Funds object in the response data

Attributes:
- None
"""
from calculation.funds.models import Funds
from calculation.models import Calculation
from core.abstract.tests import AbstractTest, generate_name


class FundsTest(AbstractTest):
    """funds related tests"""

    calculation = Calculation.objects.first()
    name = generate_name()
    parameters = {
        "description": generate_name(),
        "name": name,
        'calculation_id': str(calculation.id)
    }
    fund_id = str(Funds.objects.first().id)
    path = 'calculation/funds'

    def test_api_get(self):
        """Assert get lawyers detail"""
        self.path = f'{self.path}/{self.fund_id}'
        response = super().test_api_get()
        self.assertEqual(response.status_code, 200)
        self.assertIn('fund', response.content)
        return response.content['fund']

    @AbstractTest.execute_before_and_after
    def test_api_post_statement_fund(self):
        """Assert get lawyers detail"""

        statements = [
            ({
                 "fund_id": self.fund_id,
                 "data_base": "2020-03-23",
                 "historical_value": 200,
                 "dsr_reflexes": 100,
                 "summary": True
             }, {'corrected_value': 288.6442100028066, 'index_data_base': 2.8952660940000126,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": self.fund_id,
                 "data_base": "2011-10-10",
                 "historical_value": 555.94,
                 "dsr_reflexes": 188.94,
                 "summary": True
             }, {'corrected_value': 759.773709479113,
                 'index_data_base': 2.7310656005592993,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": self.fund_id,
                 "data_base": "2011-10-10",
                 "historical_value": 200,
                 "summary": False
             }, {'corrected_value': 204.1335457658509, 'index_data_base': 2.729264940475544,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": self.fund_id,
                 "data_base": "2011-08-10",
                 "historical_value": 2300,
                 "summary": True
             }, {'corrected_value': 2349.6542360353938, 'index_data_base': 2.726804221883394,
                 'index_recovering': 2.7856726481684837}),

        ]

        for statement, true_monetary_correction in statements:
            response = self.post('calculation/funds/funds', statement)
            new_statement = response.content['statement_funds']
            monetary_correction = new_statement['monetary_correction']
            self.assertEqual(monetary_correction['corrected_value'], true_monetary_correction['corrected_value'])
            self.assertEqual(monetary_correction['index_data_base'], true_monetary_correction['index_data_base'])
            self.assertEqual(monetary_correction['index_recovering'], true_monetary_correction['index_recovering'])
        return statements
