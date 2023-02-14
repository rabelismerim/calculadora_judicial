import json
from core.abstract.tests import AbstractTest


class ProjectTest(AbstractTest):
    """Project related tests"""

    def api_C_post_projects(self):
        """Assert post projects detail"""
        self.printl('Create Project')
        project = {
            "description": "Project test",
            "project_start": "2023-02-08",
            "project_end": "2023-02-08",
            "lawyer_id": '515e8c5d-046a-4888-96a3-623dde36db31',
            "judge_id": 'b2b791ee-86ed-4de8-b251-8e6e95705474',
            "region_id": '2431f31b-ada3-4fa3-96ee-4c20ac3f7161',
            "status": "P",
            "is_adm": True,
            "court_id": "10d1bc79-1e65-4a42-aa66-02e6b0f243b4",
            "manager_id": "1",
            "partner_id": "1",
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

        response = self.client.post(
            '/djud/api/v1/projects/', json.dumps(project), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def api_D_get_projects(self):
        """Assert get projects detail"""
        self.printl('List Project')
        response = self.client.get('/djud/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
