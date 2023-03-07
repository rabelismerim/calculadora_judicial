"""
This module defines a test class for testing the Statement API endpoints.

The StatementTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Statement objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_statements: Sends a POST request to create a new Statement object and asserts a successful response status code
- test_api_b_get_statements: Sends a GET request to retrieve a list of Statement objects and asserts a successful response status code and the presence of at least one Statement object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


class StatementTest(AbstractTest):
    """statement related tests"""

    def test_api_a_post_statements(self):
        """Assert post statements detail"""
        self.print_start('Create statements')
        statement = {
            "description": "statement"
        }
        response = self.client.post(
            '/djud/api/v1/projects/statement', statement)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created statement')

    def test_api_b_get_statements(self):
        """Assert get statements detail"""
        self.print_start('List statements')
        response = self.client.get('/djud/api/v1/projects/statement')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed statements')
        statements = response.json()['statements']
        statement = statements[0]
        self.assertGreaterEqual(len(statements), 1)
        self.print_success('Listed statements >= 1')
        self.set_project('statement_id', statement['id'])
