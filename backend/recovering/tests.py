import json
from core.abstract.tests import AbstractTest
from projects.models import Project


class RecoveringTest(AbstractTest):
    """Recovering related tests"""

    def test_api_E_post_recoverings(self):
        """Assert post recoverings detail"""
        self.printl('Create recovering')
        project = Project.objects.first()
        recovering = {
            "entity": {
                "name": "string",
                        "legal_number": "149.291.410-01"
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
            "status_support": "E",
            "project_id": str(project.id)
        }

        response = self.client.post(
            '/djud/api/v1/recovering/', json.dumps(recovering), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_api_F_get_recoverings(self):
        """Assert get recoverings detail"""
        self.printl('List recoverings')
        response = self.client.get('/djud/api/v1/recovering/')
        self.assertEqual(response.status_code, 200)
        recoverings = response.json()['recoverings']
        recovering = recoverings[0]
        self.assertGreaterEqual(len(recoverings), 1)
