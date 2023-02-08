import json
import sys
from django.core.management import color_style
from django.core.management.base import OutputWrapper
from django.test import Client, TestCase
from django.urls import reverse
from utils import get_user_model

from django.apps import apps as default_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group

User = get_user_model()


class AbstractTest(TestCase):
    """Add common methods to all testcase"""

    __user = {}
    __project = {
        "description": "Project test",
        "project_start": "2023-02-08",
        "project_end": "2023-02-08",
        "status": "P",
        "is_adm": True,
        "engagement": [
                {
                    "number": "Teste 1"
                }
        ],
    }

    def setUp(self):
        """Create User for api requests that need authentication"""
        user = {
            "email": "user@example.com",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "password": "stringst",
            "password_confirm": "stringst",
            "is_staff": True,
        }

        response = self.client.post('/djud/api/users', user)
        self.assertEqual(response.status_code, 201)
        self.set_user(json.loads(response.content)['user'])

    def get_user(self):
        """Get user"""
        return self.__user

    def set_user(self, value):
        """Update field in user, return user"""
        self.__user = value
        return self.__user

    def get_project(self):
        """Get project"""
        return self.__project

    def set_project(self, field, value):
        """Update field in project, return project"""
        self.__project[field] = value
        return self.__project

    def printl(self, msg):
        """Print in time execution"""
        self.stdout = OutputWrapper(sys.stdout)
        self.stderr = OutputWrapper(sys.stderr)
        self.style = color_style()
        self.stdout.write(self.style.SUCCESS(msg))
