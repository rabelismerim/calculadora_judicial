"""
This module defines a test class for testing the Integrations API endpoints.

The IntegrationsTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Integrations objects. The tests use the Django test client to
send HTTP requests and assert the responses. 

Methods: - test_api_a_post_integrationss: Sends a POST request to create a new Integrations object and asserts a
successful response status code - test_api_b_get_integrationss: Sends a GET request to retrieve a list of
Integrations objects and asserts a successful response status code and the presence of at least one Integrations
object in the response data

Attributes:
- None
"""
from calculation.funds.integrations.models import StatementIntegrations
from calculation.funds.models import Funds
from core.abstract.tests import AbstractTest


class FundsIntegrationsTest(AbstractTest):
    """funds related tests"""
    path = f'calculation/funds/labor/integrations/{StatementIntegrations.objects.first().id}'

    @AbstractTest.execute_before_and_after
    def test_api_post_statement_funds_integrations(self):
        """Assert get lawyers detail"""
        fund = Funds.objects.first()
        statements = [
            ({
                 "fund_id": str(fund.id),
                 'description': 'Descrição da verba 1',
                 "data_base": "2007-11-12",
                 "historical_value": 559,
                 "summary": True
             }, {'corrected_value': 594.1471867188641, 'index_data_base': 2.6208842608944427,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": str(fund.id),
                 'description': 'Descrição da verba 2',
                 "data_base": "2009-05-02",
                 "historical_value": 22800,
                 "summary": False
             }, {'corrected_value': 23735.170848147078,
                 'index_data_base': 2.675916545306843,
                 'index_recovering': 2.7856726481684837}),
        ]

        for statement, true_monetary_correction in statements:
            response = self.post('calculation/funds/labor/integrations', statement)
            new_statement = response.content['statement_funds_integrations']
            monetary_correction = new_statement['monetary_correction']
            self.assertEqual(monetary_correction['corrected_value'], true_monetary_correction['corrected_value'])
            self.assertEqual(monetary_correction['index_data_base'], true_monetary_correction['index_data_base'])
            self.assertEqual(monetary_correction['index_recovering'], true_monetary_correction['index_recovering'])
        return statements
