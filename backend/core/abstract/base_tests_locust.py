"""
The presented module imports classes and methods from other modules to define the standard behavior of load
tests using the Locust tool. It defines a main class (BaseTestsLocust) that extends an abstract class (BaseTests) and
Locust's SequentialTaskSet class. Additionally, it includes a method to perform a GET request to an API endpoint
using an authentication token defined in the TOKEN_TEST environment variable. The stop() method interrupts the
execution of the test class if it reaches the maximum limit specified in the max_execution variable.
"""
import json
import logging
import os

import locust
from locust import SequentialTaskSet, between, task
from locust.exception import InterruptTaskSet, StopUser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()
from core.abstract.base_tests import BaseTests
from config.settings import TOKEN_TEST
from utils import _


class BaseTestsLocust(BaseTests, SequentialTaskSet):
    """
    This class is responsible for defining the base behavior of Locust's test classes. It extends the BaseTests
    abstract class and the SequentialTaskSet class from Locust.

    Attributes:
        abstract (bool): Indicates that this class is abstract.
        parameters (NoneType): Not used.
        wait_time (function): Defines the wait time after each task execution.
        min_wait (int): Minimum waiting time.
        counter (int): The number of executed tasks.

    Methods:
        __init__(*args, **kwargs): Constructor method. Initializes max_execution parameter from parent class.
        load_test_get(): Task to be executed during the load test. Makes a GET request to the API endpoint,
         using the token defined in TOKEN_TEST environment variable.
        stop(): Method to interrupt the execution of the test, based on the value of __max_execution parameter.
    """
    abstract = True
    parameters = None
    wait_time = between(1, 5)
    min_wait = 0
    counter = 0
    counter_stop = 0
    __token = TOKEN_TEST

    def setUp(self):
        return

    base_url = '/juca/api/v1/'

    def get_headers(self) -> dict:
        return {'Authorization': f'Token {self.__token}', 'Content-type': 'application/json'}

    def get_base_url(self):
        return self.base_url

    def __format_url(self, path: str) -> str:
        """Formats and returns the URL for the API endpoint at `path`."""
        return f'{self.get_base_url()}{path}/'.replace('//', '/')

    def post(self, path, obj):
        """
        Sends a HTTP POST request with payload `obj` to the API endpoint specified by `path`. Returns a dictionary
        with keys 'status_code' and 'content'.
        """

        response = self.client.post(self.__format_url(path), json.dumps(obj, default=str), headers=self.get_headers(),
                                    content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        try:
            data['content'] = response.json()
        except ValueError as e:
            logging.info(e)

        return self.AttrDict(data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__max_execution = self.parent.max_execution
        self.__http_method_names = self.parent.http_method_names
        if not TOKEN_TEST:
            raise ValueError(_('Need to register a token to perform the tests'))

    def _get_headers(self) -> dict:
        return {'Authorization': f'Token {self.__token}', 'Content-type': 'application/json'}

    @task(5)
    def load_test_get(self):
        """
        Task to be executed during the load test. Makes a GET request to the API endpoint, using the token defined in
        TOKEN_TEST environment variable.
        """
        # try:

        path = self.get_path()
        if path:
            if path.endswith('None/') or path.endswith('None'):
                if hasattr(self, 'setUp'):
                    self.setUp()
                    path = self.get_path()
            self.counter += 1
            resp = self.client.get(path, headers=self._get_headers(), verify=False)
            # if str(resp.status_code).startswith('2') is False:
            # if resp.status_code != 404:
            #     print(resp.content, 'resp content\n')
            # else:
            #     print(path, 'resp content\n')
        if self.__max_execution and self.counter >= self.__max_execution:
            self.stop('get')
        # except BaseException as e:
        #     print(e, 'err')

    # @task(1)
    # def load_test_post(self):
    #     """
    #     Task to be executed during the load test. Makes a GET request to the API endpoint, using the token defined in
    #     TOKEN_TEST environment variable.
    #     """
    #     path = self.get_path_post()
    #     parameters = self.get_parameters()
    #     if path and parameters:
    #         self.counter += 1
    #         self.client.post(path, json.dumps(parameters), headers=self._get_headers())
    #     if (self.__max_execution and self.counter >= self.__max_execution) or parameters is None:
    #         self.stop('post')

    def stop(self, task_name):

        if not self.__max_execution:
            return
        raise InterruptTaskSet()

        # if self.counter_stop == len(self.__http_method_names):
        #     self.interrupt()
        #
        # if task_name in ["get", 'post']:
        #     raise InterruptTaskSet()
        #
        # self.counter_stop += 1
