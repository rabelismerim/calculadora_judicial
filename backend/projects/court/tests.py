from core.abstract.tests import AbstractTest


class CourtTest(AbstractTest):
    """court related tests"""

    def test_api_A_post_courts(self):
        """Assert post courts detail"""
        self.print_start('Create courts')
        court = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/court', court)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created court')

    def test_api_B_get_courts(self):
        """Assert get courts detail"""
        self.print_start('List courts')
        response = self.client.get('/djud/api/v1/projects/court')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed courts')
        courts = response.json()['courts']
        court = courts[0]
        self.assertGreaterEqual(len(courts), 1)
        self.print_success('Listed courts >= 1')
        self.set_project('court_id', court['id'])
