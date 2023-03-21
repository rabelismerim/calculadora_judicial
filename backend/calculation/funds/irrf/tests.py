"""
This module defines a test class for testing the Irrf API endpoints.

The IrrfTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Irrf objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_irrfs: Sends a POST request to create a new Irrf object and asserts a successful response status code
- test_api_b_get_irrfs: Sends a GET request to retrieve a list of Irrf objects and asserts a successful response status code and the presence of at least one Irrf object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class IrrfTest(AbstractTest):
#     """irrf related tests"""

#     def test_api_a_post_irrfs(self):
#         """Assert post irrfs detail"""
#         self.print_start('Create irrfs')
#         irrf = {
#             "description": "irrf"
#         }
#         response = self.client.post(
#             '/djud/api/v1/projects/irrf', irrf)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created irrf')

#     def test_api_b_get_irrfs(self):
#         """Assert get irrfs detail"""
#         self.print_start('List irrfs')
#         response = self.client.get('/djud/api/v1/projects/irrf')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed irrfs')
#         irrfs = response.json()['irrfs']
#         irrf = irrfs[0]
#         self.assertGreaterEqual(len(irrfs), 1)
#         self.print_success('Listed irrfs >= 1')
#         self.set_project('irrf_id', irrf['id'])
