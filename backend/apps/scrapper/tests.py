"""
This module defines a test class for testing the Scrapper API endpoints.

The ScrapperTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Scrapper objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_scrappers: Sends a POST request to create a new Scrapper object and asserts a successful response status code
- test_api_b_get_scrappers: Sends a GET request to retrieve a list of Scrapper objects and asserts a successful response status code and the presence of at least one Scrapper object in the response data

Attributes:
- None
"""
# from core.abstract.tests import AbstractTest


# class ScrapperTest(AbstractTest):
#     """scrapper related tests"""

#     def test_api_a_post_scrappers(self):
#         """Assert post scrappers detail"""
#         self.print_start('Create scrappers')
#         scrapper = {
#             "description": "scrapper"
#         }
#         response = self.client.post(
#             '/calculadora-judicial/api/v1/projects/scrapper', scrapper)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created scrapper')

#     def test_api_b_get_scrappers(self):
#         """Assert get scrappers detail"""
#         self.print_start('List scrappers')
#         response = self.client.get('/calculadora-judicial/api/v1/projects/scrapper')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed scrappers')
#         scrappers = response.json()['scrappers']
#         scrapper = scrappers[0]
#         self.assertGreaterEqual(len(scrappers), 1)
#         self.print_success('Listed scrappers >= 1')
#         self.set_project('scrapper_id', scrapper['id'])
