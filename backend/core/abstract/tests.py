import json
import os.path
import re
import sys
import webbrowser

from django.core.management import color_style
from django.core.management.base import OutputWrapper
from django.test import TestCase, TransactionTestCase
from config.settings import DEBUG
from utils import get_user_model
from faker import Faker


def generate_name():
    faker = Faker()
    return faker.name()


User = get_user_model()

show_result = False


class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class AbstractTest(TransactionTestCase):
    """Add common methods to all testcase"""
    stdout = OutputWrapper(sys.stdout)
    stderr = OutputWrapper(sys.stderr)
    style = color_style()
    base_url = '/djud/api/v1/'

    __user = {}
    __project = {
        "description": "Project test",
        "project_start": "2023-02-08",
        "project_end": "2023-02-08",
        # Fields expected id. dynamically set during testing
        "lawyer_id": None,
        "judge_id": None,
        "region_id": None,
        "court_id": None,
        "manager_id": None,
        "partner_id": None,
        # end
        "status": "P",
        "is_adm": True,
        "engagement": {
            "numbers": [
                "teste 1"
            ]
        },
        "recoverings": [
            {
                "entity": {
                    "name": "string",
                    "legal_number": "958.882.860-01"
                },
                "archives": [
                    {
                        "archive": {
                            "archive_json": {},
                            "description": "string"
                        }
                    }
                ],
                "date_rj_request": "2023-02-14",
                "date_rj_filing": "2023-02-14",
                "date_citation": "2023-02-14",
                "process_number": "string",
                "status": "E",
                "competence": "string",
                "status_support": "E"
            }
        ],
        "users": [{'id': '1'}]
    }

    @staticmethod
    def execute_before_and_after(func):
        stdout = OutputWrapper(sys.stdout)
        style = color_style()

        def print_start(msg):
            """Print in time execution"""
            stdout.write(style.WARNING(msg))

        def print_(msg):
            """Print in time execution"""
            stdout.write(style.ERROR(msg))

        def print_success(msg):
            """Print in time execution"""
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
                print_(f"Executando {method} {class_name} sem sucesso")
            return None

        return wrapper

    @execute_before_and_after
    def test_api_z_post(self):
        """Assert post objects detail"""
        if hasattr(self, 'path') and hasattr(self, 'parameters'):
            response = self.post(self.path, self.parameters)
            self.assertEqual(response.status_code, 201)
            return response.content

    @execute_before_and_after
    def test_api_get(self):
        """Assert get objects list detail"""
        if hasattr(self, 'path'):
            response = self.get(self.path)

            if DEBUG:
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError:
                    self.print(response)
            else:
                self.assertEqual(response.status_code, 200)
            return response

    def setUp(self):
        user_create = User.objects.filter(username='user1').first()
        if not user_create:
            user_create = User.objects.create(email="user@example1.com", username="user1",
                                              first_name="User1", last_name="User1", password="User@123",
                                              is_staff=True)
        self.assertTrue(user_create)
        user = User.objects.get(username='user1')
        self.client.force_login(user)

    def get_user(self):
        """Get user"""
        return self.__user

    def get_user_django(self):
        """Get user django"""
        user = User.objects.get(username='user1')
        self.client.force_login(user)
        return user

    def set_user(self, value):
        """Update field in user, return user"""
        self.__user = value
        return self.__user

    def print_start(self, msg):
        """Print in time execution"""
        self.stdout.write(self.style.WARNING(str(msg)))

    def print(self, msg):
        """Print in time execution"""
        self.stdout.write(self.style.ERROR(str(msg)))

    def print_success(self, msg):
        """Print in time execution"""
        self.stdout.write(self.style.SUCCESS(str(msg)))

    def __format_url(self, path: str) -> str:
        return f'{self.base_url}{path}/'.replace('//', '/')

    def post(self, path, obj):
        response = self.client.post(self.__format_url(path), json.dumps(obj), content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        dat = AttrDict(data)
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
        return AttrDict(data)

    def get(self, path):
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
        return AttrDict(data)

    def print_dict(self, obj, index=4, key='Exibir', range_=0):
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
