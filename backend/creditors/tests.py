from core.abstract.tests import AbstractTest
from rates.models import Rate
from recovering.models import Recovering


class CreditorTest(AbstractTest):
    """Creditor related tests"""

    recovering = Recovering.objects.first()
    rate = Rate.objects.first()
    path = 'creditors'
    parameters = {
        "entity": {
            "name": "string",
            "legal_number": "920.393.410-30"
        },
        "recovering_id": str(recovering.id),
        "rate_id": str(rate.id),
        "notice": {
            "classes": {
                "classe": "1"
            },
            "coins": {
                "coin": "B",
                "value": 50
            },
            "archive_json": {}
        },
        "claim_creditor": {
            "classes": {
                "classe": "1"
            },
            "coins": {
                "coin": "B",
                "value": 40
            },
            "archive_json": {}
        },
        "claim_lawyer": {
            "coins": {
                "coin": "B",
                "value": 30
            },
            "archive_json": {},
            "classes": {
                "classe": "1"
            },
        },
        "admission": "2023-02-15T15:33:53.690Z",
        "dismissal": "2023-02-15T15:33:53.690Z",
        "default_interest": 1,
        "fine": 1,
        "advocative_hours": 1,
        "description": "string"
    }
