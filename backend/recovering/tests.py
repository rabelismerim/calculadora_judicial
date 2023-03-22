from core.abstract.tests import AbstractTest
from projects.models import Project


class RecoveringTest(AbstractTest):
    """Recovering related tests"""

    project = Project.objects.first()
    parameters = {
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

    path = 'recovering'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        lawyers = response.content['recoverings']
        self.assertGreaterEqual(len(lawyers), 1)
        return lawyers
