"""
This module defines a test class for testing the Comparative API endpoints.

The ComparativeTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Comparative objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_comparatives: Sends a POST request to create a new Comparative object and asserts a successful response status code
- test_api_b_get_comparatives: Sends a GET request to retrieve a list of Comparative objects and asserts a successful response status code and the presence of at least one Comparative object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class ComparativeTest(AbstractTest):
#     """comparative related tests"""

#     def test_api_a_post_comparatives(self):
#         """Assert post comparatives detail"""
#         self.print_start('Create comparatives')
#         comparative = {
#             "description": "comparative"
#         }
#         response = self.client.post(
#             '/djud/api/v1/projects/comparative', comparative)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created comparative')

#     def test_api_b_get_comparatives(self):
#         """Assert get comparatives detail"""
#         self.print_start('List comparatives')
#         response = self.client.get('/djud/api/v1/projects/comparative')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed comparatives')
#         comparatives = response.json()['comparatives']
#         comparative = comparatives[0]
#         self.assertGreaterEqual(len(comparatives), 1)
#         self.print_success('Listed comparatives >= 1')
#         self.set_project('comparative_id', comparative['id'])
