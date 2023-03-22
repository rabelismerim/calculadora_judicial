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
from calculation.models import Calculation
from core.abstract.tests import AbstractTest


class FundsTest(AbstractTest):
    """funds related tests"""

    calculation = Calculation.objects.first()
    parameters = {
        "description": "funds",
        "name": 'Teste de verba',
        'calculation_id': str(calculation.id)
    }

    path = 'calculation/funds'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        funds = response.content['funds']
        self.assertGreaterEqual(len(funds), 1)
        return funds
