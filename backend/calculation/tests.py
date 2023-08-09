from calculation.models import Incident, Calculation
from core.abstract.tests import AbstractTest
from creditors.models import Creditor
from projects.create_project import generate_number
from rates.models import Rate


class CalculationValues:
    creditor = Creditor.objects.first()
    incident = Incident.objects.first()
    _rate = Rate.objects.first()
    if not incident:
        incident = Incident.objects.create(number=generate_number())
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
        "rate_id": str(_rate.id),
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
        "recurral_deposit": 100,
        "archive_json": {'teste': 'teste'}
    }


class CalculationTest(AbstractTest):
    """Calculation related tests"""

    creditor = Creditor.objects.first()
    parameters = CalculationValues.calculation
    path = 'calculation'
    calc = Calculation.objects.first()
    path_get = f'{path}/{calc.id if calc else None}'

    def test_api_a_get(self):
        """Assert get lawyers detail"""
        path = 'calculation/incident'
        parameters = {
            'number': generate_number()
        }
        response = self.post(path, parameters)
        self.assertEqual(response.status_code, 201)
        return response.content['incident']['number']

    def test_api_get(self):
        """Assert get lawyers detail"""
        self.path = self.path_get
        response = super().test_api_get()
        self.assertEqual(response.status_code, 200)
        self.assertIn('calculation', response.content)
        return response.content['calculation']

    base_url = '/juca/api/v2/'
    base_path = 'v2/'
