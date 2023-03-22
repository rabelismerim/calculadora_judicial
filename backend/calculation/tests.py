import json

from calculation.models import Incident
from core.abstract.tests import AbstractTest
from creditors.models import Creditor


class CalculationTest(AbstractTest):
    """Calculation related tests"""

    def test_api_E_post_calculations(self):
        """Assert post calculations detail"""
        self.print_start('Create calculation')
        creditor = Creditor.objects.first()
        incident = Incident.objects.first()
        calculation = {
            "creditor_id": str(creditor.id),
            "incident_id": str(incident.id),
            "verdict": [
                {
                    "type_calculation": {
                        "description": "string",
                        "calculation": "string"
                    },
                    "description": "string",
                    "value": 100
                }
            ]
        }

        response = self.client.post('/djud/api/v1/calculation/', json.dumps(calculation),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.print_success('Created calculation')

    def test_api_F_get_calculations(self):
        """Assert get calculations detail"""
        self.print_start('List calculations')
        response = self.client.get('/djud/api/v1/calculation/')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed calculation')
        calculations = response.json()['calculations']
        calculation = calculations[0]
        self.assertGreaterEqual(len(calculations), 1)
        self.print_success('Listed calculation >= 1')
