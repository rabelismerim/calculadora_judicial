"""
This module defines a test class for testing the Document API endpoints.

The DocumentTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Document objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_documents: Sends a POST request to create a new Document object and asserts a successful response status code
- test_api_b_get_documents: Sends a GET request to retrieve a list of Document objects and asserts a successful response status code and the presence of at least one Document object in the response data

Attributes:
- None
"""
from core.abstract.tests import AbstractTest


# class DocumentTest(AbstractTest):
#     """document related tests"""

#     def test_api_a_post_documents(self):
#         """Assert post documents detail"""
#         self.print_start('Create documents')
#         document = {
#             "description": "document"
#         }
#         response = self.client.post(
#             '/djud/api/v1/projects/document', document)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created document')

#     def test_api_b_get_documents(self):
#         """Assert get documents detail"""
#         self.print_start('List documents')
#         response = self.client.get('/djud/api/v1/projects/document')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed documents')
#         documents = response.json()['documents']
#         document = documents[0]
#         self.assertGreaterEqual(len(documents), 1)
#         self.print_success('Listed documents >= 1')
#         self.set_project('document_id', document['id'])
