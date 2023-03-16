import json
from core.abstract.tests import AbstractTest
from projects.engagement.models import ProjectEngagement
from projects.project_user.models import ProjectUser
from rates.models import Rate
from recovering.models import Recovering
from utils import get_user_model


User = get_user_model()


class CreditorTest(AbstractTest):
    """Creditor related tests"""

    def test_api_E_post_creditors(self):
        """Assert post creditors detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Criar Creditor')
        recovering = Recovering.objects.first()
        rate = Rate.objects.first()
        creditor = {
            "entity": {
                "name": "string",
                "legal_number": "920.393.410-30"
            },
            "recovering_id": str(recovering.id),
            "rate_id": str(rate.id),
            "notice": {
                "classes": {
                    "classe": "1"
                },
                "coins": {
                    "coin": "B",
                    "value": 0
                },
                "archive_json": {}
            },
            "claim_creditor": {
                "classes": {
                    "classe": "1"
                },
                "coins": {
                    "coin": "B",
                    "value": 0
                },
                "archive_json": {}
            },
            "claim_lawyer": {
                "coins": {
                    "coin": "B",
                    "value": 0
                },
                "archive_json": {},
                "classes": {
                    "classe": "1"
                },
            },
            "admission": "2023-02-15T15:33:53.690Z",
            "dismissal": "2023-02-15T15:33:53.690Z",
            "default_interest": 0,
            "fine": 0,
            "advocative_hours": 0,
            "description": "string"
        }

        response = self.client.post(
            '/djud/api/v1/creditors/', json.dumps(creditor), content_type="application/json")
        # self.print(response.json())
        self.assertEqual(response.status_code, 201)
        self.print_success('Created creditor')
        content = json.loads(response.content)
        self.set_project('creditor_id', content['creditor']['id'])

    def test_api_F_get_creditors(self):
        """Assert get creditors detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Lista de Creditors')
        response = self.client.get('/djud/api/v1/creditors/')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed creditors')
