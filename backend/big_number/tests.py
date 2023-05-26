"""
This module defines a test class for testing the BigNumber API endpoints.

The BigNumberTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing BigNumber objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_big_numbers: Sends a POST request to create a new BigNumber object and asserts a successful response status code
- test_api_b_get_big_numbers: Sends a GET request to retrieve a list of BigNumber objects and asserts a successful response status code and the presence of at least one BigNumber object in the response data

Attributes:
- None
"""
# from core.abstract.tests import AbstractTest


# class BigNumberTest(AbstractTest):
#     """big_number related tests"""

#     def test_api_a_post_big_numbers(self):
#         """Assert post big_numbers detail"""
#         self.print_start('Create big_numbers')
#         big_number = {
#             "description": "big_number"
#         }
#         response = self.client.post(
#             '/juca/api/v1/projects/big_number', big_number)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created big_number')

#     def test_api_b_get_big_numbers(self):
#         """Assert get big_numbers detail"""
#         self.print_start('List big_numbers')
#         response = self.client.get('/juca/api/v1/projects/big_number')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed big_numbers')
#         big_numbers = response.json()['big_numbers']
#         big_number = big_numbers[0]
#         self.assertGreaterEqual(len(big_numbers), 1)
#         self.print_success('Listed big_numbers >= 1')
#         self.set_project('big_number_id', big_number['id'])
