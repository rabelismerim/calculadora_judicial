from core.abstract.tests import AbstractTest


class ProjectUserTest(AbstractTest):
    """Project User related tests"""

    def test_api_E_post_project_users(self):
        """Assert post project_users detail"""
        self.printl('Create Project User')
        project_user = {
            "user": self.get_user()['id'],
        }
        response = self.client.post(
            '/djud/api/v1/projects/project_user', project_user)
        self.assertEqual(response.status_code, 201)

    def test_api_F_get_project_users(self):
        """Assert get Project User detail"""
        self.printl('List Project Users')
        response = self.client.get('/djud/api/v1/projects/project_user')
        self.assertEqual(response.status_code, 200)
