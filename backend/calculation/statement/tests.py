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


class StatementTest(AbstractTest):
    """statement related tests"""
    calculation = None

    # def setUp(self):
    #     super().setUp()
    #     self._new_project()

    def _new_project(self, date_request, date_filling, date_citation):
        self._set_project(date_request, date_filling, date_citation)
        self._set_creditor()
        self._set_calculation()
        self._set_funds()

    def get_statement(self):
        response = self.get(f'calculation/statement/')
        self.assertEqual(response.status_code, 200)
        calcs = response.content['statements']
        print(len(calcs))

    def _assert_calc(self, statement_result):
        response = self.get(f'calculation/{self.calculation.id}/')
        self.assertEqual(response.status_code, 200)
        calc = AttrDict(response.content['calculation'])
        comparative = self._compare_statements(calc.statement, statement_result)
        print(comparative, 'comparative\n')
        self.assertTrue(comparative)

    def _compare_statements(self, statement, statement_result):
        # for key, value in statement_result.items():
        #     if isinstance(value, dict):
        #         comparison_result, (mismatch_key, mismatch_value) = self._compare_statements(statement.get(key, {}), value)
        #         if not comparison_result:
        #             return False, (mismatch_key, mismatch_value)
        #     elif isinstance(value, list):
        #         comparison_result = all(
        #             self._compare_statements(i_stmt, i_stmt_result)
        #             for i_stmt, i_stmt_result in zip(statement.get(key, []), value)
        #         )
        #         if not comparison_result:
        #             return False, (key, (i, (k, v)) for i, (k, v) in enumerate(statement_result.get(key, [])))
        #     else:
        #         if statement.get(key) != value:
        #             return False, (key, value)
        # return True, (None, None)
        for key, value in statement_result.items():
            if isinstance(value, dict):
                if not self._compare_statements(statement.get(key, {}), value):
                    return False
            elif isinstance(value, list):
                if not all(self._compare_statements(i_stmt, i_stmt_result) for i_stmt, i_stmt_result in zip(statement.get(key, []), value)):
                    return False
            else:
                if statement.get(key) != value:
                    return False
        return True

    def _set_project(self, date_request, date_filling, date_citation):
        data_project = get_data_project()
        data_project["date_rj_request"] = date_request
        data_project["date_rj_filing"] = date_filling
        data_project["date_citation"] = date_citation
        response = self.post('projects', data_project)
        self.assertEqual(response.status_code, 201)
        self.project = AttrDict(response.content['project'])

    def _set_creditor(self):
        creditor = CreditorValues().get_creditor()
        creditor['entity']['name'] = generate_name()
        creditor['entity']['legal_number'] = cpf_generator()
        creditor['recovering_id'] = self.project['recoverings'][0]['id']
        response = self.post('creditors', creditor)
        self.assertEqual(response.status_code, 201)
        self.creditor = AttrDict(response.content['creditor'])

    def _set_calculation(self):
        calculation = CalculationValues.calculation
        calculation['creditor_id'] = self.creditor['id']

        response = self.post('calculation', calculation)
        self.assertEqual(response.status_code, 201)
        self.calculation = AttrDict(response.content['calculation'])

    def _set_funds(self):
        fund = {
            "description": generate_name(),
            "name": generate_name(),
            'calculation_id': str(self.calculation.id)
        }

        response = self.post('calculation/funds', fund)
        self.assertEqual(response.status_code, 201)
        self.fund = AttrDict(response.content['funds'])

    def test_a_funds(self):
        date_request = "2015-06-09"
        date_filling = "2010-10-14"
        date_citation = "2010-10-14"
        self._new_project(date_request, date_filling, date_citation)

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
                    "description_display": "Dias em atraso",
                    "value": 1675,
                    "description": "D"
                },
                "default_interest": {
                    "value": 2011.2315165497669
                },
                "default_interest_due": {
                    "description_display": "Total após juros de mora",
                    "value": 5613.437217832931,
                    "description": "T"
                },
                "funds_description": [
                    {
                        "total": 3602.205701283164,
                    }
                ],
                "description_display": "Total atualizado",
                "status_display": "Concluído",
                "status": "C",
                "description": "A",
                "total": 3602.205701283164
            },
            "statement_pj": None,
            "lawyer": None,
            "conclusion_display": "Impugnação",
            "conclusion": "I"
        }
        self._assert_statements(statements)
        self.get_statement()
        self._assert_calc(statement_result)
        return statements

    def _assert_statements(self, statements):
        for statement, true_monetary_correction in statements:
            response = self.post('calculation/funds/funds', statement)
            new_statement = response.content['statement_funds']
            monetary_correction = new_statement['monetary_correction']
            self.assertEqual(monetary_correction['corrected_value'], true_monetary_correction['corrected_value'])
            self.assertEqual(monetary_correction['index_data_base'], true_monetary_correction['index_data_base'])
            self.assertEqual(monetary_correction['index_recovering'], true_monetary_correction['index_recovering'])
