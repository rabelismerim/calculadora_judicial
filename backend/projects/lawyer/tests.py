from core.abstract.tests import AbstractTest


class LawyerTest(AbstractTest):
    """lawyer related tests"""

    def test_api_C_post_lawyers(self):
        """Assert post lawyers detail"""
        self.print_start('Create lawyer')
        lawyer = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/lawyer', lawyer)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created lawyer')

    def test_api_D_get_lawyers(self):
        """Assert get lawyers detail"""
        self.print_start('List lawyers')
        response = self.client.get('/djud/api/v1/projects/lawyer')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed lawyers')
        lawyers = response.json()['lawyers']
        lawyer = lawyers[0]
        self.assertGreaterEqual(len(lawyers), 1)
        self.print_success('Listed lawyers >= 1')
        self.set_project('lawyer_id', lawyer['id'])
