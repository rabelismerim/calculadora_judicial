from core.abstract.tests import AbstractTest
from projects.create_project import cpf_generator
from projects.models import Project


class RecoveringTest(AbstractTest):
    """Recovering related tests"""

    project = Project.objects.first()
    parameters = {
        "entity": {
            "name": "string",
            "legal_number": cpf_generator()
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
        """Assert get recovering detail"""
        response = super().test_api_get()
        recovering = response.content['recoverings']
        self.assertGreaterEqual(len(recovering), 1)
        return recovering

    def test_api_z_post(self):
        """Assert get recovering detail"""
        super().test_api_z_post()
        response = self.post(self.path, self.parameters)  # recovering already registered
        self.assertEqual(response.status_code, 400)

    def test_api_post(self):
        """Assert post invalid legal number"""
        parameters = self.parameters
        parameters['entity']['legal_number'] = 'invalid legal number'
        response = self.post(self.path, parameters)  # invalid legal number
        self.assertEqual(response.status_code, 400)

    base_url = '/djud/api/v2/'
    base_path = 'v2/'
