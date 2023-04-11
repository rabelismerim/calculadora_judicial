from core.abstract.tests import AbstractTest, generate_name


class LawyerTest(AbstractTest):
    """lawyer related tests"""
    parameters = {
        "description": generate_name()
    }
    path = 'projects/lawyer/'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        lawyers = response.content['lawyers']
        self.assertGreaterEqual(len(lawyers), 1)
        return lawyers
