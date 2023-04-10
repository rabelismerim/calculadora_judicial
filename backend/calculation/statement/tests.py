# """
# This module defines a test class for testing the Statement API endpoints.
#
# The StatementTest class inherits from the AbstractTest class and includes two methods for testing
# the HTTP POST and GET methods for managing Statement objects. The tests use the Django test client to
# send HTTP requests and assert the responses.
#
# Methods: - test_api_a_post_statements: Sends a POST request to create a new Statement object and asserts a successful
# response status code - test_api_b_get_statements: Sends a GET request to retrieve a list of Statement objects and
# asserts a successful response status code and the presence of at least one Statement object in the response data
#
# Attributes:
# - None
# """
# from core.abstract.tests import AbstractTest
# from projects.create_project import get_data_project
# from projects.models import Project
#
#
# class StatementTest(AbstractTest):
#     """statement related tests"""
#
#     data_project = get_data_project()
#     data_project["date_rj_request"] = "2023-03-02"
#     data_project["date_rj_filing"] = "2023-03-02"
#     data_project["date_citation"] = "2023-03-02"
#
#     new_project = Project.objects.create(**data_project)
#     print(new_project, 'new project\n')
#     # parameters = {
#     #     "description": "statement"
#     # }
#     #
#     # path = 'calculations/statement'
#     #
#     # def test_api_get(self):
#     #     """Assert get statements detail"""
#     #     response = super().test_api_get()
#     #     objs = response.content['statements']
#     #     self.assertGreaterEqual(len(objs), 1)
#     #     return objs
