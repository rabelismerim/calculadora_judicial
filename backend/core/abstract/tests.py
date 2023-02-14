import json
import sys
from django.core.management import color_style
from django.core.management.base import OutputWrapper
from django.test import TestCase
from utils import get_user_model

User = get_user_model()


class AbstractTest(TestCase):
    """Add common methods to all testcase"""
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
        "engagement":  {
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
        user_detail = json.loads(response.content)['user']
        self.set_user(user_detail)
        self.set_project('manager_id', user_detail['id'])
        self.set_project('partner_id', user_detail['id'])

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
        self.__check_run_project(field, value)
        return self.__project

    def printl(self, msg):
        """Print in time execution"""
        self.stdout = OutputWrapper(sys.stdout)
        self.stderr = OutputWrapper(sys.stderr)
        self.style = color_style()
        self.stdout.write(self.style.SUCCESS(msg))

    def __check_run_project(self, field, value):
        project_complete_keys = ['judge_id',
                                 'lawyer_id', 'region_id', 'court_id', 'manager_id', 'partner_id', 'users']
        project_complete = True
        for key in project_complete_keys:
            if not self.__project.get(key):
                project_complete = False
                break

        if project_complete and not self.__project.get('project_complete'):
            self.set_project('project_complete', True)
            project = self.get_project()
            project[field] = value
            response = self.client.post(
                '/djud/api/v1/projects/', json.dumps(project), content_type="application/json")
            self.assertEqual(response.status_code, 201)
            project = response.json()['project']
            self.set_project('project_id', project['id'])
