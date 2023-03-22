"""
This module defines a test class for testing the Funds API endpoints.

The FundsTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Funds objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_fundss: Sends a POST request to create a new Funds object and asserts a successful response status code
- test_api_b_get_fundss: Sends a GET request to retrieve a list of Funds objects and asserts a successful response status code and the presence of at least one Funds object in the response data

Attributes:
- None
"""
import json

from calculation.models import Calculation
from core.abstract.tests import AbstractTest
from utils import get_user_model

User = get_user_model()


class FundsTest(AbstractTest):
    """funds related tests"""

    def test_api_a_post_fundss(self):
        """Assert post fundss detail"""
        user = User.objects.get(username='user1')
        calculation = Calculation.objects.first()
        self.client.force_login(user)
        self.print_start('Create fundss')
        funds = {
            "description": "funds",
            "name": 'Teste de verba',
            'calculation_id': str(calculation.id)
        }
        response = self.client.post('/djud/api/v1/calculation/funds/', json.dumps(funds),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.print_success('Created funds')

    def test_api_b_get_fundss(self):
        """Assert get fundss detail"""
        user = User.objects.get(username='user1')
        self.client.force_login(user)
        self.print_start('List funds')
        response = self.client.get('/djud/api/v1/calculation/funds/')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed funds')
        funds = response.json()['funds']
        self.assertGreaterEqual(len(funds), 1)
        fund = funds[0]
        self.print_success('Listed funds >= 1')
        self.set_project('funds_id', fund['id'])
