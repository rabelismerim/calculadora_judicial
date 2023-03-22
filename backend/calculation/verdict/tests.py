import random
from calculation.models import Calculation
from core.abstract.tests import AbstractTest

str_rd = ''
while len(str_rd) <= 10:
    str_rd += '%c' % random.randint(97, 122)


class VerdictTest(AbstractTest):
    """Verdict related tests"""

    calculation = Calculation.objects.first()
    parameters = {
        "type_calculation": {
            "description": "string",
            "calculation": "string"
        },
        "calculation_id": str(calculation.id),
        "description": str_rd,
        "value": 0
    }

    path = 'calculation/verdict'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        verdicts = response.content['verdicts']
        self.assertGreaterEqual(len(verdicts), 1)
        return verdicts
