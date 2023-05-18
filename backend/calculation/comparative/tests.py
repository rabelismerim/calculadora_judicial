# """
# This module defines a test class for testing the Comparative API endpoints.
#
# The ComparativeTest class inherits from the AbstractTest class and includes two methods for testing
# the HTTP POST and GET methods for managing Comparative objects. The tests use the Django test client to
# send HTTP requests and assert the responses.
#
# Methods: - test_api_a_post_comparatives: Sends a POST request to create a new Comparative object and asserts a
# successful response status code - test_api_b_get_comparatives: Sends a GET request to retrieve a list of Comparative
# objects and asserts a successful response status code and the presence of at least one Comparative object in the
# response data
#
# Attributes:
# - None
# """
# from core.abstract.tests import AbstractTest
#
#
# class ComparativeTest(AbstractTest):
#     """comparative related tests"""
#
#     parameters = {
#         "description": "comparative"
#     }
#
#     path = 'calculation/comparative'
#
#     def test_api_get(self):
#         """Assert get comparatives detail"""
#         response = super().test_api_get()
#         objs = response.content['comparatives']
#         self.assertGreaterEqual(len(objs), 1)
#         return objs
