"""
This module defines a test class for testing the StatementPJ API endpoints.

The StatementPJTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing StatementPJ objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_statementPJs: Sends a POST request to create a new StatementPJ object and asserts a successful response status code
- test_api_b_get_statementPJs: Sends a GET request to retrieve a list of StatementPJ objects and asserts a successful response status code and the presence of at least one StatementPJ object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


class StatementPJTest(AbstractTest):
    """statementPJ related tests"""

    def test_api_a_post_statementPJs(self):
        """Assert post statement_pfs detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create statement_pfs')
        statementPJ = {
            "description": "statementPJ"
        }
        response = self.client.post(
            '/djud/api/v1/calculations/statementPJ', statementPJ)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created statementPJ')

    def test_api_b_get_statementPJs(self):
        """Assert get statementPJs detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List statement_pfs')
        response = self.client.get('/djud/api/v1/calculations/statement_pf')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed statementPJs')
        statementPJs = response.json()['statement_pfs']
        statementPJ = statementPJs[0]
        self.assertGreaterEqual(len(statementPJs), 1)
        self.print_success('Listed statementPJs >= 1')
        self.set_project('statement_pf_id', statementPJ['id'])
