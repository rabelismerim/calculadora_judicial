"""This module is a unit testing class for Django that inherits from the TransactionTestCase test class. It defines
test_api_z_post() and test_api_get() methods to test HTTP POST and GET requests, respectively. The class also has
several helper methods, such as print_start(), print(), print_success(), post(), get(), print_dict() and _write_html(
), to print data and format it for display in HTML. To use it, inherit the AbstractTest class inside your django
app's tests file. Define the path value, which is the url to be consumed, and parameters, which would be the payload
for the post. You can also define the methods to be used within the http_method_names list"""

import json
import os.path
import sys
import webbrowser

from django.core.management import color_style
from django.core.management.base import OutputWrapper
from django.test import TransactionTestCase
from config.settings import DEBUG
from utils import get_user_model, secret_number
from core.abstract.base_tests import BaseTests

User = get_user_model()

show_result = False


class BaseTestsDjango(BaseTests, TransactionTestCase):
    """ Base test class for Django URLS.
        Methods:
            test_api_z_post(): Assert detail of HTTP POST requests.
            test_api_get(): Assert detail of HTTP GET requests.
            setUp(): Setup method for test class. Creates a test user if one doesn't exist already, logs in the user,
                and sets the `keep_db` flag based on command line arguments.
            get_user() -> User: Returns the currently logged in user.
            get_user_django() -> User: Logs in the user and returns the user object.
            set_user(value) -> User: Updates the currently logged in user to `value` and returns the updated user object.
            print_start(msg): Prints `msg` in the console with a warning style.
            print(msg): Prints `msg` in the console with an error style.
            print_success(msg): Prints `msg` in the console with a success style.
            __format_url(path: str) -> str: Formats and returns the URL for the API endpoint at `path`.
            __create_payload(path, obj, method, code): Creates a payload file for API testing (used for debugging).
            post(path, obj) -> dict: Sends a HTTP POST request with payload `obj` to the API endpoint specified by
                `path`. Returns a dictionary with keys 'status_code' and 'content'.
            get(path) -> dict: Sends a HTTP GET request to the API endpoint specified by `path`. Returns a
                dictionary with keys 'status_code' and 'content'.
            print_dict(obj, index=4, key='Exibir', range_=0) -> str: Formats and returns a string representation
                of the dictionary object `obj`. Used to display dictionaries in a formatted way in HTML.
            _write_html(data, key, show=False): Writes the HTML output of HTTP requests and displays it in the default
                browser. If `show_results` flag is False, returns immediately without writing anything.
    """
    stdout = OutputWrapper(sys.stdout)
    stderr = OutputWrapper(sys.stderr)
    style = color_style()
    base_url = '/djud/api/v1/'

    def get_base_url(self):
        return self.base_url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keep_db = '--keepdb' in sys.argv

    @BaseTests.execute_before_and_after
    def test_api_z_post(self):
        """Assert detail of HTTP POST requests."""
        if hasattr(self, 'path') and hasattr(self, 'parameters') and self.has_post():
            response = self.post(self.path, self.parameters)
            if response.status_code == 404:
                self.print('\n\n')
                self.print(self.path)
                self.print('\n\n')

            if DEBUG:
                try:
                    self.assertEqual(response.status_code, 201)
                except AssertionError:
                    self.print(response)
            else:
                self.assertEqual(response.status_code, 201)
            return response.content

    @BaseTests.execute_before_and_after
    def test_api_get(self):
        """Assert detail of HTTP GET requests"""
        if hasattr(self, 'path') and self.has_get():
            path = getattr(self, 'path_get', None) or getattr(self, 'path', None)
            response = self.get(path)
            if response.status_code == 404:
                self.print('\n\n')
                self.print(self.path)
                self.print('\n\n')

            if DEBUG:
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError:
                    self.print(response)
            else:
                self.assertEqual(response.status_code, 200)
            return response

    def setUp(self):
        """
        Setup method for test class. Creates a test user if one doesn't exist already, logs in the user, and sets the
        `keep_db` flag based on command line arguments.
        """
        user_create = User.objects.filter(username='user1').first()
        if not user_create:
            user_create = User.objects.create(email="user@example1.com", username="user1",
                                              first_name="User1", last_name="User1", password="User@123",
                                              is_staff=True)
        self.assertTrue(user_create)
        user = User.objects.get(username='user1')
        self.client.force_login(user)

    # def get_user(self):
    #     """Get user"""
    #     return self.__user
    #
    def get_user_django(self):
        """Get user django"""
        user = User.objects.get(username='user1')
        self.client.force_login(user)
        return user

    # def set_user(self, value):
    #     """Update field in user, return user"""
    #     self.__user = value
    #     return self.__user

    def print_start(self, msg):
        """rints `msg` in the console with a warning style."""
        self.stdout.write(self.style.WARNING(str(msg)))

    def print(self, msg):
        """Prints `msg` in the console with an error style."""
        self.stdout.write(self.style.ERROR(str(msg)))

    def print_success(self, msg):
        """Prints `msg` in the console with a success style."""
        self.stdout.write(self.style.SUCCESS(str(msg)))

    def __format_url(self, path: str) -> str:
        """Formats and returns the URL for the API endpoint at `path`."""
        return f'{self.get_base_url()}{path}/'.replace('//', '/')

    def __create_payload(self, path, obj, method, code):
        """Creates a payload file for API testing (used for debugging)"""
        if True:
            return
        if DEBUG is False:
            return
        payload = {
            'url': self.__format_url(path),
            'data': obj,
        }

        if os.path.exists('payload') is False:
            os.mkdir('payload')
        with open(f'payload/payload_{method}_{code}_{path.replace("/", "_")}_{secret_number(1, 1000)}.json',
                  mode='w',
                  encoding='utf-8') as f:
            f.write(json.dumps(payload))

    def post(self, path, obj):
        """
        Sends a HTTP POST request with payload `obj` to the API endpoint specified by `path`. Returns a dictionary
        with keys 'status_code' and 'content'.
        """
        response = self.client.post(self.__format_url(path), json.dumps(obj, default=str),
                                    content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        dat = self.AttrDict(data)
        try:
            data['content'] = response.json()
            is_json = True
        except ValueError:
            is_json = False
        ab = response.status_code in [200, 201]
        if ab is False:
            self.print(dat.content)
        if is_json:
            keys = list(data['content'].keys())
            key = keys[0]
            values = [dict(data['content'][key])]
            self._write_html(values, key)

        dt = {
            'sent': obj,
            'received': data['content'],
        }
        self.__create_payload(path, dt, 'post', response.status_code)
        return self.AttrDict(data)

    def get(self, path):
        """
        Sends a HTTP GET request to the API endpoint specified by `path`. Returns a dictionary with keys
        'status_code' and 'content'.
        """
        response = self.client.get(self.__format_url(path), content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        try:
            data['content'] = response.json()
            is_json = True
        except ValueError:
            is_json = False

        if is_json:
            keys = list(data['content'].keys())
            key = keys[0]
            values = data['content'][key]
            self._write_html(values, key)

        self.__create_payload(path, data['content'], 'get', response.status_code)
        return self.AttrDict(data)

    def print_dict(self, obj, index=4, key='Exibir', range_=0):
        """
        Formats and returns a string representation of the dictionary object `obj`. Used to display dictionaries in a
        formatted way in HTML.
        """
        key = key.capitalize()
        card_body = f""" 
                <a href="#{key}{range_}" class="list-group-item collapsed" data-toggle="collapse" 
                                data-parent="#sidebar" aria-expanded="false"> 
                <i class="fa fa-dashboard"></i> 
                <h5 class="hidden-sm-down">{key}</h5>
            </a>
            <div id="{key}{range_}" class='collapse' data-toggle='collapse' aria-expanded="false">\n"""

        index += 1
        if index > 6:
            index = 6
        if isinstance(obj, str):
            return ''
        items = list(obj.items())
        for i in range(len(items)):
            key = items[i][0]
            value = items[i][1]
            next_elm = None
            if i < len(items) - 1:
                next_elm = items[i + 1]

            elm = "<div class='card-body pt-1 pb-1'>\n"

            if key in ['created_at', 'updated_at', 'update_user', 'create_user', 'id']:
                continue

            if str(key).endswith('_id'):
                continue
            # elm = f"""<
            #         div class='row'>
            #             <div class='col-sm-6'>
            #                 "<h{index} class='card-title'>{key}</h{index}>\n"
            #             </div>
            #             <div class='col-sm-6'>
            #                 "<p class='card-text'>{value}</p>\n"
            #             </div>
            #         </div>
            # """

            # if next_elm:
            #     if not isinstance(next_elm[1], (dict, list)):
            #         elm += f"<h{index} class='card-title'>{key}</h{index}>\n"
            # else:
            #     elm += f"<h{index} class='card-title'>{key}</h{index}>\n"

            if isinstance(value, dict):
                elm += self.print_dict(value, index, key)
            elif isinstance(value, list):
                card_body += "".join(self.print_dict(elm, index, key) for elm in value)
            else:
                if next_elm:
                    if not isinstance(next_elm[1], (dict, list)):
                        # elm += f"<p class='card-text'>{value}</p>\n"
                        elm += f"""<div class='row'>
                                        <div class='col-sm-6'>
                                            <h{index} class='card-title'>{key}</h{index}>\n
                                        </div>
                                        <div class='col-sm-6'>
                                            <p class='card-text'>{value}</p>\n
                                        </div>
                                    </div>
                                    """
                else:
                    elm += f"""<div class='row'>
                                    <div class='col-sm-6'>
                                        <h{index} class='card-title'>{key}</h{index}>\n
                                    </div>
                                    <div class='col-sm-6'>
                                        <p class='card-text'>{value}</p>\n
                                    </div>
                                </div>
                            """

            elm += "</div>\n"
            card_body += elm
        card_body += "</div>\n"
        return card_body

    def _write_html(self, data, key, show=False):
        """Writes the HTML output of HTTP requests and displays it in the default browser. If `show_results` flag is
        False, returns immediately without writing anything.
        """

        if any([show_result, show]) is False:
            return
        card_body = ''
        card_row = """
                     <div class="col-sm-12 p-5">
                        <div class="card" id="sidebar">
                                {}
                        </div>
                    </div>
                    """
        if isinstance(data, list) is False:
            data = [data]
        for i in range(len(data)):
            card_body += card_row.format(self.print_dict(data[i], key=key, range_=i))

        message = f"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>JUCA Api Tests</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
                        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
                    </head>
                    </head>
                    <body>
                         <div class="container">
                            <div class="row">
                               {card_body}
                            </div>
                        </div>
                    </body>
                </html>
                """

        filename = os.path.join(os.getcwd(), 'tests.html')
        f = open(filename, 'w')
        f.write(message)
        f.close()

        webbrowser.open_new_tab(filename)

        self.print('opened')

        while True:
            next_ = input('Aperte a tecla q para sair\n')
            if next_ == 'q':
                break
