"""
The presented module imports classes and methods from other modules to define the standard behavior of load tests
using the Locust tool. It defines a main class (BaseTestsLocust) that extends an abstract class (BaseTests) and
Locust's SequentialTaskSet class. Additionally, it includes a method to perform a GET request to an API endpoint
using an authentication token defined in the TOKEN_TEST environment variable. The stop() method interrupts the
execution of the test class if it reaches the maximum limit specified in the max_execution variable.

The Locust interface can be accessed via the URL http://localhost:8089/.

When you open this page, you will see the "Swarm" tab that displays a form to define the number of users (clients)
and the arrival rate (hatch rate) that will be used in the simulation.

After filling in this information, click on the "Start swarming" button to start the simulation.

On the "Stop" tab, you can pause or end the simulation.

The "Charts" tab displays real-time graphs showing the performance of the tested application. You can work with
different types of charts by selecting the desired options from the drop-down menu.

The "Table" tab displays a table with detailed information about each request sent during the simulation. This
feature can be useful for analyzing which routes and endpoints are being most demanded.

The "Errors" tab displays information about errors that occurred while running the simulation. This tab can help you
identify and fix problems with your application.

In summary, Locust's interface allows controlling and monitoring the execution of load tests, as well as viewing
detailed information about the performance of the tested application.
"""
import os
#

from locust import HttpUser, between
import importlib

import locust
from locust import SequentialTaskSet
from locust.exception import StopUser

import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{django_moa}.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings')
import django

django.setup()


def _get_classes(filepath):
    """
    Get classes from filepath.

    :param filepath: Path of the file that contains the classes.
    :type filepath: str
    :return: List of classes.
    :rtype: List[type]
    """
    spec = importlib.util.spec_from_file_location("module.name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names = dir(module)
    classes = [getattr(module, name) for name in names if
               isinstance(getattr(module, name), type) and
               hasattr(getattr(module, name), 'min_wait') and
               name != 'AbstractTest' and
               name.endswith('Test')]
    return classes


def get_classes():
    """
    Get all tests classes from the "tests.py" files inside the current working directory.

    :return: List with all test classes.
    :rtype: List[type]
    """
    files_path = []
    classes = set()
    for subdir, dirs, files in os.walk(os.path.join(os.getcwd(), '..')):
        if "venv" in dirs:
            dirs.remove("venv")
        for file_name in files:
            if file_name == "tests.py":
                file_path = os.path.join(subdir, file_name)
                classes.update(_get_classes(file_path))
                files_path.append(file_path)
    return list(classes)


class RequestsTask(SequentialTaskSet):
    tasks = get_classes()

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of RequestTask.

        :param args: Positional arguments for SequentialTaskSet.
        :param kwargs: Keyword arguments for SequentialTaskSet.
        """
        super().__init__(*args, **kwargs)
        self.max_execution = self.parent.max_execution
        self.http_method_names = self.parent.http_method_names

    def on_start(self):
        """
        Initializes all test classes and runs them.
        Raises StopUser exception when finished.
        """
        for task_class in self.tasks:
            try:
                task_instance = task_class(self)
                if task_instance:
                    task_instance.run()
            except (locust.exception.RescheduleTaskImmediately, AttributeError, locust.exception.InterruptTaskSet):
                pass
        raise StopUser()


class UnlimitedRequests(HttpUser):
    """
    A HttpUser subclass that sends unlimited requests.

    This class will execute unlimited requests to the endpoints found for testing. Each user represents an endpoint.
    The more users, the more endpoints will be tested Attributes: tasks (list): A list of task classes to be
    executed. wait_time (function): A function that returns the time to wait between each request. max_execution (
    int): A int indicating a maximum number of requests to be sent.
    """
    tasks: list = get_classes()
    wait_time: float = between(1, 5)
    max_execution: None or int = None
    http_method_names = ['get', 'post']


class MaxRequests(HttpUser):
    """
    A HttpUser subclass that sends max requests.

    This class will execute limited requests to the endpoints found for testing. Each user represents an endpoint.
    The more users, the more endpoints will be tested Attributes: tasks (list): A list of task classes to be
    executed. wait_time (function): A function that returns the time to wait between each request. max_execution (
    int): A int indicating a maximum number of requests to be sent.
    """
    tasks: list = [RequestsTask]
    wait_time: float = between(0.1, 0.5)
    max_execution: None or int = 10
    http_method_names = ['get', 'post']


if __name__ == '__main__':
    from locust.main import main
    import sys

    sys.argv = ["locust", "-f", os.path.join(os.getcwd(), 'main.py'), '--class-picker']
    main()
