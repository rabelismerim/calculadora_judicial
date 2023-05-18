# """
# This module defines a test class for testing the StatementPF API endpoints.
#
# The StatementPFTest class inherits from the AbstractTest class and includes two methods for testing
# the HTTP POST and GET methods for managing StatementPF objects. The tests use the Django test client to
# send HTTP requests and assert the responses.
#
# Methods:
# - test_api_a_post_statementPFs: Sends a POST request to create a new StatementPF object and asserts a successful response status code
# - test_api_b_get_statementPFs: Sends a GET request to retrieve a list of StatementPF objects and asserts a successful response status code and the presence of at least one StatementPF object in the response data
#
# Attributes:
# - None
# """
# from core.abstract.tests import AbstractTest
# from utils import get_user_model
#
#
# User = get_user_model()
#
#
# class StatementPFTest(AbstractTest):
#     """statementPF related tests"""
#
#     def test_api_a_post_statementPFs(self):
#         """Assert post statement_pfs detail"""
#         user = User.objects.get(username='user1')
#         self.client.force_login(user)
#         self.print_start('Create statement_pfs')
#         statementPF = {
#             "description": "statementPF"
#         }
#         response = self.client.post(
#             '/juca/api/v1/calculations/statementPF', statementPF)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created statementPF')
#
#     def test_api_b_get_statementPFs(self):
#         """Assert get statementPFs detail"""
#         user = User.objects.get(username='user1')
#         self.client.force_login(user)
#         self.print_start('List statement_pfs')
#         response = self.client.get('/juca/api/v1/calculations/statement_pf')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed statementPFs')
#         statementPFs = response.json()['statement_pfs']
#         statementPF = statementPFs[0]
#         self.assertGreaterEqual(len(statementPFs), 1)
#         self.print_success('Listed statementPFs >= 1')
#         self.set_project('statement_pf_id', statementPF['id'])
