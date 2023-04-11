from core.abstract.tests import AbstractTest, generate_name
from projects.create_project import cpf_generator
from projects.models import Project
from rates.models import Rate
from recovering.models import Recovering


class CreditorValues:
    _recovering = Recovering.objects.first()
    _rate = Rate.objects.first()

    creditor = {
        "entity": {
            "name": generate_name(),
            "legal_number": cpf_generator()
        },
        "recovering_id": str(_recovering.id),
        "rate_id": str(_rate.id),
        "notice_aj": [{
            "classes": {
                "classe": "1"
            },
            "coins": {
                "coin": "B",
                "value": 50
            },
            "archive_json": {}
        }],
        "claim_creditor": [{
            "classes": {
                "classe": "1"
            },
            "coins": {
                "coin": "B",
                "value": 40
            },
            "archive_json": {}
        }],
        "claim_lawyer": {
            "coins": {
                "coin": "B",
                "value": 30
            },
            "archive_json": {},
            "classes": {
                "classe": "1"
            },
        },
        "admission": "2023-02-15T15:33:53.690Z",
        "dismissal": "2023-02-15T15:33:53.690Z",
        "default_interest": 1,
        "fine": 1,
        "advocative_hours": 1,
        "occurrence": "A",
        "description": "string"
    }

    def get_creditor(self):
        creditor = self.creditor
        creditor['entity']['name'] = generate_name()
        creditor['entity']['legal_number'] = cpf_generator()
        return creditor


class CreditorTest(AbstractTest):
    """Creditor related tests"""

    path = 'creditors'
    parameters = CreditorValues().get_creditor()

    def setUp(self):
        set_up = super().setUp()
        self.parameters = CreditorValues().get_creditor()
        self.parameters['entity']['name'] = generate_name()
        self.parameters['entity']['legal_number'] = cpf_generator()
        return set_up

    def test_api_get(self):
        """Assert get lawyers detail"""
        project = Project.objects.first()
        response = self.get(f'creditors/project/{project.id}')
        self.assertEqual(response.status_code, 200)
