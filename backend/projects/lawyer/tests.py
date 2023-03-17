from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


class LawyerTest(AbstractTest):
    """lawyer related tests"""

    def test_api_C_post_lawyers(self):
        """Assert post lawyers detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create lawyer')
        lawyer = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/lawyer', lawyer)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created lawyer')

    def test_api_D_get_lawyers(self):
        """Assert get lawyers detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List lawyers')
        response = self.client.get('/djud/api/v1/projects/lawyer')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed lawyers')
        lawyers = response.json()['lawyers']
        lawyer = lawyers[0]
        self.assertGreaterEqual(len(lawyers), 1)
        self.print_success('Listed lawyers >= 1')
        self.set_project('lawyer_id', lawyer['id'])
