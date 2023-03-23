from core.abstract.tests import AbstractTest


class ProjectUserTest(AbstractTest):
    """Project User related tests"""

    path = 'projects/project_user'

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
