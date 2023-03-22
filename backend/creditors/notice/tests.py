from core.abstract.tests import AbstractTest
from creditors.models import Creditor


class NoticeTest(AbstractTest):
    """Notice related tests"""

    creditor = Creditor.objects.first()
    notice = creditor.get_notice()
    if notice:
        notice.delete()
    parameters = {
        "classes": {
            "classe": "1"
        },
        "coins": {
            "coin": "B",
            "value": 1
        },
        "archive_json": {},
        "creditor_id": str(creditor.id)
    }
    path = 'creditors/notice'
