from core.abstract.tests import AbstractTest
from projects.create_project import get_data_project


class ProjectTest(AbstractTest):
    """Project related tests"""

    @AbstractTest.execute_before_and_after
    def test_api_a_post_projects(self):
        """Assert post projects detail"""
        project = get_data_project(str(self.get_user_django().id))
        response = self.post('projects', project)
        self.assertEqual(response.status_code, 201)

        response = self.post('projects', project)  # Engagement already registered
        self.assertEqual(response.status_code, 400)

    @AbstractTest.execute_before_and_after
    def test_api_b_get_projects(self):
        """Assert get projects detail"""
        response = self.get('projects')
        self.assertEqual(response.status_code, 200)
