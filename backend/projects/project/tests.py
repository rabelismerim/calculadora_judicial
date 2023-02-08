import json
from core.abstract.tests import AbstractTest


class ProjectTest(AbstractTest):
    """Project related tests"""

    def test_api_C_post_projects(self):
        """Assert post projects detail"""
        self.printl('Create Project')
        project = {
            "description": "Project test",
            "project_start": "2023-02-08",
            "project_end": "2023-02-08",
            "lawyer_id": 'b8aa5d2d-caa6-43b4-aba6-4174e5febff7',
            "judge_id": '6d283934-dfd0-4160-9c83-4317d16f1080',
            "region_id": '7c27ae09-c893-454d-b48d-d477b4381c87',
            "status": "P",
            "is_adm": True,
            "engagement": [
                {
                    "number": "Teste 1"
                }
            ],
            "users": [{'id': 4}]
        }

        response = self.client.post(
            '/djud/api/v1/projects/project', json.dumps(project), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        self.printl(content)
        self.set_project('project_id', content['project']['id'])

    def test_api_D_get_projects(self):
        """Assert get projects detail"""
        self.printl('List Project')
        response = self.client.get('/djud/api/v1/projects/project')
        content = json.loads(response.content)
        self.printl(content)
        self.assertEqual(response.status_code, 200)
