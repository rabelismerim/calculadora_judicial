import json
import re
import sys
import time
import uuid

from django.core.management import color_style
from django.core.management.base import OutputWrapper
from django.test import TestCase
from config.settings import DEBUG
from utils import get_user_model

User = get_user_model()

import pandas as pd


class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class AbstractTest(TestCase):
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
        self.stdout.write(self.style.WARNING(msg))

    def print(self, msg):
        """Print in time execution"""
        self.stdout.write(self.style.ERROR(msg))

    def print_success(self, msg):
        """Print in time execution"""
        self.stdout.write(self.style.SUCCESS(msg))

    def __format_url(self, path: str) -> str:
        return f'{self.base_url}{path}/'.replace('//', '/')

    def post(self, path, obj):
        response = self.client.post(self.__format_url(path), json.dumps(obj), content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        try:
            data['content'] = response.json()
            is_json = True
        except ValueError:
            is_json = False

        # if is_json:
        #     keys = list(data['content'].keys())
        #     key = keys[0]
        #     values = [dict(data['content'][key])]
        #     df = pd.DataFrame(values)

            # df.to_excel(f'file_{uuid.uuid4()}.xlsx')
        return AttrDict(data)

    def get(self, path):
        response = self.client.get(self.__format_url(path), content_type="application/json")
        data = {'status_code': response.status_code, 'content': response.content}
        try:
            data['content'] = response.json()
        except ValueError:
            pass
        return AttrDict(data)
