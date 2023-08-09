"""
This module defines a test class for testing the File API endpoints.

The FileTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing File objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_files: Sends a POST request to create a new File object and asserts a successful response status code
- test_api_b_get_files: Sends a GET request to retrieve a list of File objects and asserts a successful response status code and the presence of at least one File object in the response data

Attributes:
- None
"""
# from core.abstract.tests import AbstractTest


# class FileTest(AbstractTest):
#     """file related tests"""

#     def test_api_a_post_files(self):
#         """Assert post files detail"""
#         self.print_start('Create files')
#         file = {
#             "description": "file"
#         }
#         response = self.client.post(
#             '/juca/api/v1/projects/file', file)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created file')

#     def test_api_b_get_files(self):
#         """Assert get files detail"""
#         self.print_start('List files')
#         response = self.client.get('/juca/api/v1/projects/file')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed files')
#         files = response.json()['files']
#         file = files[0]
#         self.assertGreaterEqual(len(files), 1)
#         self.print_success('Listed files >= 1')
#         self.set_project('file_id', file['id'])
