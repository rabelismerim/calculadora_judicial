from core.abstract.tests import AbstractTest


class LawyerTest(AbstractTest):
    """lawyer related tests"""
    parameters = {
        "description": "Name Juiz 1"
    }
    path = 'projects/lawyer/'

    def test_api_get(self):
        """Assert get lawyers detail"""
        response = super().test_api_get()
        lawyers = response.content['lawyers']
        self.assertGreaterEqual(len(lawyers), 1)
        return lawyers
