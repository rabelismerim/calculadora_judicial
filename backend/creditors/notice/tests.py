import json
from core.abstract.tests import AbstractTest
from creditors.models import Creditor


class NoticeTest(AbstractTest):
    """Notice related tests"""

    def test_api_E_post_notices(self):
        """Assert post notices detail"""
        self.print_start('Create notice')
        creditor = Creditor.objects.first()
        notice = creditor.get_notice()
        if notice:
            notice.delete()
        notice = {
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

        response = self.client.post(
            '/djud/api/v1/creditors/notice', json.dumps(notice), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.print_success('Created notice')

    def test_api_F_get_notices(self):
        """Assert get notices detail"""
        self.print_start('List notices')
        response = self.client.get(
            '/djud/api/v1/creditors/notice')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed notice')
        notices = response.json()['notices']
        notice = notices[0]
        self.assertGreaterEqual(len(notices), 1)
        self.print_success('Listed notice >= 1')
