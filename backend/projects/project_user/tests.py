from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


class ProjectUserTest(AbstractTest):
    """Project User related tests"""

    def test_api_E_post_project_users(self):
        """Assert post project users detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create Project User')
        project_user = {
            "user": self.get_user()['id'],
        }
        response = self.client.post(
            '/djud/api/v1/projects/project_user', project_user)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created project user')

    def test_api_F_get_project_users(self):
        """Assert get Project User detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List project users')
        response = self.client.get('/djud/api/v1/projects/project_user')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed project users')
        project_users = response.json()['project_users']
        project_user = project_users[0]
        self.assertGreaterEqual(len(project_users), 1)
        self.print_success('Listed project users >= 1')
        self.set_project('users', [{'id': project_user['id']}])
