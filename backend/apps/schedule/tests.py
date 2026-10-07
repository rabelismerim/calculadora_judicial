"""
This module defines a test class for testing the Schedule API endpoints.

The ScheduleTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Schedule objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods:
- test_api_a_post_schedules: Sends a POST request to create a new Schedule object and asserts a successful response status code
- test_api_b_get_schedules: Sends a GET request to retrieve a list of Schedule objects and asserts a successful response status code and the presence of at least one Schedule object in the response data

Attributes:
- None
"""
# from core.abstract.tests import AbstractTest


# class ScheduleTest(AbstractTest):
#     """schedule related tests"""

#     def test_api_a_post_schedules(self):
#         """Assert post schedules detail"""
#         self.print_start('Create schedules')
#         schedule = {
#             "description": "schedule"
#         }
#         response = self.client.post(
#             '/calculadora-judicial/api/v1/projects/schedule', schedule)
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created schedule')

#     def test_api_b_get_schedules(self):
#         """Assert get schedules detail"""
#         self.print_start('List schedules')
#         response = self.client.get('/calculadora-judicial/api/v1/projects/schedule')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed schedules')
#         schedules = response.json()['schedules']
#         schedule = schedules[0]
#         self.assertGreaterEqual(len(schedules), 1)
#         self.print_success('Listed schedules >= 1')
#         self.set_project('schedule_id', schedule['id'])
