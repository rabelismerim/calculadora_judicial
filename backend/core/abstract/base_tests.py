import logging
import re
import sys

from django.core.management import color_style
from django.core.management.base import OutputWrapper
from faker import Faker


class BaseTests:
    """
    A base class for tests with common methods and attributes to tests.

    Attributes:
        faker (Faker): An instance of Faker used to generate fake data.

    Methods:
        execute_before_and_after(func): A decorator that prints start, success or error messages
            before and after the execution of a test method.
        has_get(): Returns a boolean indicating whether the test has a GET method or not.
        get_path(): Returns the path for the test to be executed, adding a trailing slash if it's missing.
        has_post(): Returns a boolean indicating whether the test has a POST method or not.
        generate_name(): Generates a fake name using Faker library.
    """
    faker = Faker()
    base_path = 'v1/'

    @staticmethod
    def execute_before_and_after(func):
        """
        A decorator that prints start, success or error messages before and after the execution of a test method.

        Args:
            func (function): The function to be decorated.

        :return:
            The decorated function.
        """
        stdout = OutputWrapper(sys.stdout)
        style = color_style()

        def print_start(msg):
            """Prints a message with a warning style."""
            stdout.write(style.WARNING(msg))

        def print_(msg):
            """Prints a message with an error style."""
            stdout.write(style.ERROR(msg))

        def print_success(msg):
            """Prints a message with a success style."""
            stdout.write(style.SUCCESS(msg))

        def wrapper(*args, **kwargs):
            class_name = str(args[0]).split('.')[-1].replace(')', '')
            method = 'get' if re.findall(r'_get', str(args[0])) else 'post'
            try:
                print_start(f"Executando {method} {class_name}")
                resultado = func(*args, **kwargs)
                print_success(f"Executado {method} {class_name} com sucesso")
                return resultado
            except AssertionError:
                logging.info(f"Executando {method} {class_name} sem sucesso")
            return None

        return wrapper

    def has_get(self):
        """Returns a boolean indicating whether the test has a GET method or not."""
        if hasattr(self, 'http_method_names'):
            return 'get' in self.http_method_names
        return True

    def get_path(self):
        """Returns the path for the test to be executed, adding a trailing slash if it's missing."""
        path = getattr(self, 'path_get', None) or getattr(self, 'path', None)
        if path and self.has_get():
            if str(path).endswith('/') is False:
                path = str(path) + '/'
        return f'{self.base_path}{path}'

    def get_path_post(self):
        """Returns the path for the test to be executed, adding a trailing slash if it's missing."""
        path = getattr(self, 'path', None)
        if path and self.has_post():
            if str(path).endswith('/') is False:
                path = str(path) + '/'
        return path

    def get_parameters(self) -> dict or None:
        """Returns the path for the test to be executed, adding a trailing slash if it's missing."""
        if hasattr(self, 'parameters'):
            return self.parameters

    def has_post(self):
        """Returns a boolean indicating whether the test has a POST method or not."""
        if hasattr(self, 'http_method_names'):
            return 'post' in self.http_method_names
        return True

    class AttrDict(dict):
        """
        A subclass of dict that allows its content to be accessed as attributes.

        Methods:
            __getattr__(attr): Returns the value of an attribute. If it doesn't exist, raises an AttributeError.
            __setattr__(attr, value): Sets the value of an attribute.
        """

        def __getattr__(self, attr):
            return self[attr]

        def __setattr__(self, attr, value):
            self[attr] = value

    def generate_name(self):
        """Generates a fake name using Faker library."""
        return self.faker.name()
