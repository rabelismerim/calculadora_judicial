"""
This module defines a test class for testing the Irrf API endpoints.

The IrrfTest class inherits from the AbstractTest class and includes two methods for testing
the HTTP POST and GET methods for managing Irrf objects. The tests use the Django test client to
send HTTP requests and assert the responses.

Methods:
- test_api_a_post_irrfs: Sends a POST request to create a new Irrf object and asserts a successful response status code
- test_api_b_get_irrfs: Sends a GET request to retrieve a list of Irrf objects and asserts a successful response status code and the presence of at least one Irrf object in the response data

Attributes:
- None
"""
from calculation.funds.irrf.models import FundIRRF
from calculation.models import Calculation
from core.abstract.tests import AbstractTest, generate_name
from rates.models import Rate


class IrrfTest(AbstractTest):
    """irrf related tests"""
    http_method_names = ['post', 'get']

    path = 'calculation/funds/irrf'
    path_get = f'calculation/funds/irrf/{FundIRRF.objects.first().id}'
    parameters = {
        "classes": {
            "classe": "1"
        },
        "coins": {
            "coin": "B",
            "value": 200
        },
        "archive_json": {},
        "rate_id": str(Rate.objects.first().id),
        "calculation_id": str(
            Calculation.objects.filter(creditor__physical_person=True, funddocument__isnull=True).first().id),
        "name": generate_name(),
        "months_period": 1
    }
