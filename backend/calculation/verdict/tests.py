import json
import random
from calculation.models import Calculation
from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


str_rd = ''
while (len(str_rd) <= 10):
    str_rd += '%c' % random.randint(97, 122)


class VerdictTest(AbstractTest):
    """Verdict related tests"""

    def test_api_E_post_verdicts(self):
        """Assert post verdicts detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create verdict')
        calculation = Calculation.objects.first()
        verdict = {
            "type_calculation": {
                "description": "string",
                "calculation": "string"
            },
            "calculation_id": str(calculation.id),
            "description": str_rd,
            "value": 0
        }

        response = self.client.post(
            '/djud/api/v1/calculation/verdict', json.dumps(verdict), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.print_success('Created verdict')

    def test_api_F_get_verdicts(self):
        """Assert get verdicts detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List verdicts')
        response = self.client.get('/djud/api/v1/calculation/verdict')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed verdicts')
        verdicts = response.json()['verdicts']
        verdict = verdicts[0]
        self.assertGreaterEqual(len(verdicts), 1)
        self.print_success('Listed verdicts >= 1')
