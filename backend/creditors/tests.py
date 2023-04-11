import random

from core.abstract.tests import AbstractTest, generate_name
from projects.create_project import cpf_generator
from projects.models import Project
from rates.models import Rate
from recovering.models import Recovering


class CreditorValues:

    def __get_creditor_by_rate(self, rate):
        _recovering = Recovering.objects.first()
        _rate = Rate.objects.filter(index__icontains=rate).first()

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
                    "value": random.randint(1, 2000)
                },
                "archive_json": {}
            }],
            "claim_creditor": [{
                "classes": {
                    "classe": "1"
                },
                "coins": {
                    "coin": "B",
                    "value": random.randint(1, 2000)
                },
                "archive_json": {}
            }],
            "claim_lawyer": {
                "coins": {
                    "coin": "B",
                    "value": random.randint(1, 2000)
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
        return creditor

    def get_creditor(self, rate='TST'):
        creditor = self.__get_creditor_by_rate(rate)
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
