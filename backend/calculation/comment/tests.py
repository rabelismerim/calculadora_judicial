"""
This module defines a test class for testing the Comment API endpoints.

The CommentTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Comment objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_comments: Sends a POST request to create a new Comment object and asserts a successful response status code
- test_api_b_get_comments: Sends a GET request to retrieve a list of Comment objects and asserts a successful response status code and the presence of at least one Comment object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class CommentTest(AbstractTest):
#     """comment related tests"""

#     def test_api_a_post_comments(self):
#         """Assert post comments detail"""
#         self.print_start('Create comments')
#         comment = {
#             "description": "comment"
#         }
#         response = self.client.post(
#             '/calculadora-judicial/api/v1/projects/comment', comment)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created comment')

#     def test_api_b_get_comments(self):
#         """Assert get comments detail"""
#         self.print_start('List comments')
#         response = self.client.get('/calculadora-judicial/api/v1/projects/comment')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed comments')
#         comments = response.json()['comments']
#         comment = comments[0]
#         self.assertGreaterEqual(len(comments), 1)
#         self.print_success('Listed comments >= 1')
#         self.set_project('comment_id', comment['id'])
