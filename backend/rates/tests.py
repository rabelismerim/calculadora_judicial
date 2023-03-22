from core.abstract.tests import AbstractTest
from rates.models import get_aliquot_by_tax


class RatesTest(AbstractTest):
    """Rates related tests"""

    @AbstractTest.execute_before_and_after
    def test_api_get(self):
        """Assert get Rates detail"""
        values = (
            (0, 0, 0), (5, 0, 0), (1903.98, 0, 0),  # Alíquotas de - até 1903.08
            (1903.99, 142.80, 7.5), (2826.65, 142.80, 7.5),  # Alíquotas de 1903.99 - até 2826.65
            (2826.66, 354.80, 15), (3751.05, 354.80, 15),  # Alíquotas de 2826.66 - até 3751.05
            (3751.06, 636.13, 22.5), (4664.68, 636.13, 22.5),  # Alíquotas de 3751.06 - até 4664.68
            (4664.69, 869.36, 27.5), (5000.00, 869.36, 27.5),)  # Alíquotas de 4664.69 para cima

        for value, deduction, aliquot in values:
            self.assertEqual(get_aliquot_by_tax(value).deduction, deduction)
            self.assertEqual(get_aliquot_by_tax(value).aliquot, aliquot)
