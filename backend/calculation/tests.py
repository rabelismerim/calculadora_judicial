from calculation.models import Incident, Calculation
from core.abstract.tests import AbstractTest
from creditors.models import Creditor


class CalculationValues:
    creditor = Creditor.objects.first()
    incident = Incident.objects.first()
    calculation = {
        "classes": {
            "classe": "1"
        },
        "coins": {
            "coin": "B",
            "value": 0
        },
        "creditor_id": str(creditor.id),
        "incident_id": str(incident.id),
        "verdict": [
            {
                "type_calculation": {
                    "description": "string",
                    "calculation": "string"
                },
                "description": "string",
                "value": 200
            }
        ],
        "appeal_credit": True,
        "appeal_deposit": True,
        "has_advocative_hours": True,
        "date_credit_auth": "2023-04-10",
        "has_edital": True,
        "recurral_deposit": 100,
        "archive_json": {'teste': 'teste'}
    }


class CalculationTest(AbstractTest):
    """Calculation related tests"""

    creditor = Creditor.objects.first()
    incident = Incident.objects.first()
    parameters = CalculationValues.calculation
    path = 'calculation'

    def test_api_get(self):
        """Assert get lawyers detail"""
        self.path = f'{self.path}/{Calculation.objects.first().id}'
        response = super().test_api_get()
        self.assertEqual(response.status_code, 200)
        self.assertIn('calculation', response.content)
        return response.content['calculation']
