import json
from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


class JudgeTest(AbstractTest):
    """judge related tests"""

    def test_api_A_post_judges(self):
        """Assert post judges detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create lawyers')
        judge = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/judge', judge)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created judge')

    def test_api_B_get_judges(self):
        """Assert get judges detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List lawyers')
        response = self.client.get('/djud/api/v1/projects/judge')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed judges')
        judges = response.json()['judges']
        judge = judges[0]
        self.assertGreaterEqual(len(judges), 1)
        self.print_success('Listed judges >= 1')
        self.set_project('judge_id', judge['id'])
