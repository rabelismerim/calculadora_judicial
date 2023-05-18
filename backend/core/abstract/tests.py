import sys
from faker import Faker


# TODO: utilizar a funcao em self
def generate_name():
    faker = Faker()
    return faker.name()


if str(sys.argv[0]).endswith('manage.py'):
    from core.abstract.base_tests_django import BaseTestsDjango as Base
else:
    from core.abstract.base_tests_locust import BaseTestsLocust as Base


class AbstractTest(Base):
    """
    This module provides an abstract class for testing.
    If the script is run with 'manage.py', it uses BaseTestsDjango class from core.abstract.base_tests_django module.
    Otherwise, it uses BaseTestsLocust class from core.abstract.base_tests_locust module.

    The base define what the type of test will be. BaseTestsDjango tests the endpoints and does the validations.
    BaseTestsLocust performs load testing on endpoints, simulates multiple users and measures how the platform is doing

    Classes:
    - AbstractTest: An abstract test class that inherits from BaseTestsDjango or BaseTestsLocust, depending on the script being run.
    """
