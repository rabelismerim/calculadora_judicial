import json
from core.abstract.tests import AbstractTest
from projects.create_project import get_data_project
from utils import get_user_model


User = get_user_model()


class ProjectTest(AbstractTest):
    """Project related tests"""

    def test_api_C_post_projects(self):
        """Assert post projects detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create Project')
        project = get_data_project(str(user.id))

        response = self.client.post('/djud/api/v1/projects/', json.dumps(project), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_api_D_get_projects(self):
        """Assert get projects detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List Project')
        response = self.client.get('/djud/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
