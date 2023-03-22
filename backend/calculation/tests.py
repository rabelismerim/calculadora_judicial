import json

from calculation.models import Incident
from core.abstract.tests import AbstractTest
from creditors.models import Creditor


class CalculationTest(AbstractTest):
    """Calculation related tests"""

    creditor = Creditor.objects.first()
    incident = Incident.objects.first()
    parameters = {
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

    path = 'calculation'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        objs = response.content['calculations']
        self.assertGreaterEqual(len(objs), 1)
        return objs
