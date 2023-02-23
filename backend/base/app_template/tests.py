"""
This module defines a test class for testing the {{app_name | title}} API endpoints.

The {{app_name | title}}Test class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing {{app_name | title}} objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_{{app_name}}s: Sends a POST request to create a new {{app_name | title}} object and asserts a successful response status code
- test_api_b_get_{{app_name}}s: Sends a GET request to retrieve a list of {{app_name | title}} objects and asserts a successful response status code and the presence of at least one {{app_name | title}} object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class {{app_name | title}}Test(AbstractTest):
#     """{{app_name}} related tests"""

#     def test_api_a_post_{{app_name}}s(self):
#         """Assert post {{app_name}}s detail"""
#         self.print_start('Create {{app_name}}s')
#         {{app_name}} = {
#             "description": "{{app_name}}"
#         }
#         response = self.client.post(
#             '/djud/api/v1/projects/{{app_name}}', {{app_name}})
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created {{app_name}}')

#     def test_api_b_get_{{app_name}}s(self):
#         """Assert get {{app_name}}s detail"""
#         self.print_start('List {{app_name}}s')
#         response = self.client.get('/djud/api/v1/projects/{{app_name}}')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed {{app_name}}s')
#         {{app_name}}s = response.json()['{{app_name}}s']
#         {{app_name}} = {{app_name}}s[0]
#         self.assertGreaterEqual(len({{app_name}}s), 1)
#         self.print_success('Listed {{app_name}}s >= 1')
#         self.set_project('{{app_name}}_id', {{app_name}}['id'])
