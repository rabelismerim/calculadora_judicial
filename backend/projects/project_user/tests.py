from core.abstract.tests import AbstractTest
from utils import get_user_model

User = get_user_model()


class ProjectUserTest(AbstractTest):
    """Project User related tests"""

    path = 'projects/project_user'
    def get_user_django(self):
        """Get user django"""
        user = User.objects.get(username='user1')
        self.client.force_login(user)
        return user

    def setUp(self, *args, **kwargs):
        super().setUp()
        self.parameters = {
            "user": self.get_user_django().id,
        }
    #

    # def test_api_get(self):
    #     """Assert get Project User detail"""
    #     response = super().test_api_get()
    #     objs = response.content['project_user']
    #     self.assertGreaterEqual(len(objs), 1)
    #     return objs
