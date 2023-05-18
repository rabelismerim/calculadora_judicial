"""
This module defines a test class for testing the Premise API endpoints.

The PremiseTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Premise objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_premises: Sends a POST request to create a new Premise object and asserts a successful response status code
- test_api_b_get_premises: Sends a GET request to retrieve a list of Premise objects and asserts a successful response status code and the presence of at least one Premise object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class PremiseTest(AbstractTest):
#     """premise related tests"""

#     def test_api_a_post_premises(self):
#         """Assert post premises detail"""
#         self.print_start('Create premises')
#         premise = {
#             "description": "premise"
#         }
#         response = self.client.post(
#             '/juca/api/v1/projects/premise', premise)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created premise')

#     def test_api_b_get_premises(self):
#         """Assert get premises detail"""
#         self.print_start('List premises')
#         response = self.client.get('/juca/api/v1/projects/premise')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed premises')
#         premises = response.json()['premises']
#         premise = premises[0]
#         self.assertGreaterEqual(len(premises), 1)
#         self.print_success('Listed premises >= 1')
#         self.set_project('premise_id', premise['id'])
