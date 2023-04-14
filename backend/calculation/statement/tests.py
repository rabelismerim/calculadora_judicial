"""
This module defines a test class for testing the Statement API endpoints.

The StatementTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Statement objects. The tests use the Django test client to
send HTTP requests and assert the responses.

Methods: - test_api_a_post_statements: Sends a POST request to create a new Statement object and asserts a successful
response status code - test_api_b_get_statements: Sends a GET request to retrieve a list of Statement objects and
asserts a successful response status code and the presence of at least one Statement object in the response data

Attributes:
- None
"""
from calculation.tests import CalculationValues
from core.abstract.tests import AbstractTest, AttrDict, generate_name
from creditors.tests import CreditorValues
from projects.create_project import get_data_project, cpf_generator
from utils import _


class StatementTest(AbstractTest):
    """Represents tests related to statement calculations and correction"""

    def _new_project(self, date_request, date_filling, date_citation, rate):
        """Creates a new project with specified dates and interest rate"""
        self._set_project(date_request, date_filling, date_citation)
        self._set_creditor(rate)
        self._set_calculation()
        self._set_funds()

    def _assert_calc(self, statement_result):
        """
        Makes a request to get the calculation with the current statement and compares it to the provided statement
        result
        """

        response = self.get(f'calculation/{self.calculation.id}/')
        self.assertEqual(response.status_code, 200)
        calc = AttrDict(response.content['calculation'])
        comparative = self._compare_statements(calc.statement, statement_result)
        total = len(comparative)
        if total > 0:
            self.print(comparative)
        if self.keep_db:
            self.assertEqual(0, len(comparative))

    def _compare_statements(self, statement, statement_result, errors=None):
        """Recursively compares a statement object to a provided statement result object and returns any errors"""

        if errors is None:
            errors = []
        for key, value in statement_result.items():
            if isinstance(value, dict):
                errors = self._compare_statements(statement.get(key, {}), value, errors)
            elif isinstance(value, list):
                for i, (i_stmt, i_stmt_result) in enumerate(zip(statement.get(key, []), value)):
                    errors = self._compare_statements(i_stmt, i_stmt_result, errors)
            else:
                if statement.get(key) != value:
                    errors.append({'field_error': key, 'value': value, 'expected': statement.get(key)})
        return errors

    def _set_project(self, date_request, date_filling, date_citation):
        """Creates a new project with the specified dates"""

        data_project = get_data_project()
        data_project["date_rj_request"] = date_request
        data_project["date_rj_filing"] = date_filling
        data_project["date_citation"] = date_citation
        response = self.post('projects', data_project)
        self.assertEqual(response.status_code, 201)
        self.project = AttrDict(response.content['project'])

    def _set_creditor(self, rate):
        """Creates a new creditor with the specified rate for the project"""

        creditor = CreditorValues().get_creditor(rate)
        creditor['entity']['name'] = generate_name()
        creditor['entity']['legal_number'] = cpf_generator()
        creditor['recovering_id'] = self.project['recoverings'][0]['id']
        response = self.post('creditors', creditor)
        self.assertEqual(response.status_code, 201)
        self.creditor = AttrDict(response.content['creditor'])

    def _set_calculation(self):
        """Creates a new calculation object for the creditor"""

        calculation = CalculationValues.calculation
        calculation['creditor_id'] = self.creditor['id']

        response = self.post('calculation', calculation)
        self.assertEqual(response.status_code, 201)
        self.calculation = AttrDict(response.content['calculation'])

    def _set_funds(self):
        """Creates a new fund object associated with the calculation"""

        fund = {
            "description": generate_name(),
            "name": generate_name(),
            'calculation_id': str(self.calculation.id)
        }

        response = self.post('calculation/funds', fund)
        self.assertEqual(response.status_code, 201)
        self.fund = AttrDict(response.content['funds'])

    def test_a_funds(self):
        """Runs a series of tests using a fund and a set of statements with expected results"""

        date_request = "2015-06-09"
        date_filling = "2010-10-14"
        date_citation = "2010-10-14"
        rate = 'TST'
        self._new_project(date_request, date_filling, date_citation, rate)

        fund = self.fund
        statements = [
            ({
                 "fund_id": str(fund.id),
                 "data_base": "2020-03-23",
                 "historical_value": 200,
                 "dsr_reflexes": 100,
                 "summary": True
             }, {'corrected_value': 288.6442100028066, 'index_data_base': 2.8952660940000126,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": str(fund.id),
                 "data_base": "2011-10-10",
                 "historical_value": 555.94,
                 "dsr_reflexes": 188.94,
                 "summary": True
             }, {'corrected_value': 759.773709479113,
                 'index_data_base': 2.7310656005592993,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": str(fund.id),
                 "data_base": "2011-10-10",
                 "historical_value": 200,
                 "summary": False
             }, {'corrected_value': 204.1335457658509, 'index_data_base': 2.729264940475544,
                 'index_recovering': 2.7856726481684837}),
            ({
                 "fund_id": str(fund.id),
                 "data_base": "2011-08-10",
                 "historical_value": 2300,
                 "summary": True
             }, {'corrected_value': 2349.6542360353938, 'index_data_base': 2.726804221883394,
                 'index_recovering': 2.7856726481684837}),

        ]
        statement_result = {
            "statement_pf": {
                "tax_days": {
                    "description_display": _("Delayed days"),
                    "value": 1675,
                    "description": "D"
                },
                "default_interest": {
                    "value": 2011.2315165497669
                },
                "default_interest_due": {
                    "description_display": _("Total after default interest"),
                    "value": 5613.437217832931,
                    "description": "T"
                },
                "funds_description": [
                    {
                        "total": 3602.205701283164,
                    }
                ],
                "description_display": _("Updated total"),
                "status_display": _("Concluded"),
                "status": "C",
                "description": "A",
                "total": 3602.205701283164
            },
            "statement_pj": None,
            "lawyer": None,
            "conclusion_display": _("Impugnment"),
            "conclusion": "I"
        }
        self._assert_statements(statements)
        self._assert_calc(statement_result)
        return statements

    def _assert_statements(self, statements):
        """
        Sends a set of statement objects, checks the response statement, and compares monetary correction values to
        expected results.
        """

        for statement, true_monetary_correction in statements:
            response = self.post('calculation/funds/funds', statement)
            new_statement = response.content['statement_funds']
            monetary_correction = new_statement['monetary_correction']
            self.assertEqual(monetary_correction['corrected_value'], true_monetary_correction['corrected_value'])
            self.assertEqual(monetary_correction['index_data_base'], true_monetary_correction['index_data_base'])
            self.assertEqual(monetary_correction['index_recovering'], true_monetary_correction['index_recovering'])
