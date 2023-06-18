import json
import random

from core.abstract.tests import AbstractTest, generate_name
from projects.create_project import cpf_generator
from projects.models import Project
from rates.models import Rate
from recovering.models import Recovering
from utils import secret_number


class CreditorValues:

    def __get_creditor_by_rate(self, rate, physical_person: bool = True):
        _recovering = Recovering.objects.first()
        _rate = Rate.objects.filter(index__icontains=rate).first()

        creditor = {
            "entity": {
                "name": generate_name(),
                "legal_number": cpf_generator()
            },
            "physical_person": physical_person,
            "recovering_id": str(_recovering.id),
            "rate_id": str(_rate.id),
            "notice_aj": [{
                "classes": {
                    "classe": "1"
                },
                "coins": {
                    "coin": "B",
                    "value": secret_number(1, 2000)
                },
                "archive_json": {}
            }],
            "claim_creditor": [{
                "classes": {
                    "classe": "1"
                },
                "coins": {
                    "coin": "B",
                    "value": secret_number(1, 2000)
                },
                "archive_json": {}
            }],
            "claim_lawyer": {
                "coins": {
                    "coin": "B",
                    "value": secret_number(1, 2000)
                },
                "archive_json": {},
                "classes": {
                    "classe": "1"
                },
            },
            "admission": "2012-02-15",
            "dismissal": "2012-02-15",
            "default_interest": 1,
            "fine": 1,
            "advocative_hours": 1,
            "occurrence": "A",
            "description": "string"
        }
        return creditor

    def get_creditor(self, rate='TST', physical_person=True):
        creditor = self.__get_creditor_by_rate(rate, physical_person)
        return creditor


class CreditorTest(AbstractTest):
    """Creditor related tests"""

    path = 'creditors'
    path_get = f'creditors/project/{Project.objects.first().id}'
    parameters = CreditorValues().get_creditor()

    def setUp(self):
        set_up = super().setUp()
        self.parameters = CreditorValues().get_creditor()
        self.parameters['physical_person'] = False
        self.parameters['entity']['name'] = generate_name()
        self.parameters['entity']['legal_number'] = cpf_generator()

        self.parameters = CreditorValues().get_creditor()
        self.parameters['entity']['name'] = generate_name()
        self.parameters['entity']['legal_number'] = cpf_generator()
        return set_up

    def test_api_get(self):
        """Assert get lawyers detail"""
        project = Project.objects.first()
        response = self.get(f'creditors/project/{project.id}')
        self.assertEqual(response.status_code, 200)

    def test_api_z_post(self):
        """Assert get lawyers detail"""
        super().test_api_z_post()
        response = self.post(self.path, self.parameters)  # creditor already registered
        self.assertEqual(response.status_code, 400)
