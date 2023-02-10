from core.abstract.tests import AbstractTest


class JudgeTest(AbstractTest):
    """judge related tests"""

    def test_api_A_post_judges(self):
        """Assert post judges detail"""
        self.printl('Create lawyers')
        judge = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/judge', judge)
        self.assertEqual(response.status_code, 201)

    def test_api_B_get_judges(self):
        """Assert get judges detail"""
        self.printl('List lawyers')
        response = self.client.get('/djud/api/v1/projects/judge')
        self.assertEqual(response.status_code, 200)
