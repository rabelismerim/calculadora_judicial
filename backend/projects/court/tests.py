from core.abstract.tests import AbstractTest


class CourtTest(AbstractTest):
    """Court related tests"""

    parameters = {
        "description": "Name Juiz 1"
    }
    path = 'projects/court'

    def test_api_get(self):
        """Assert get courts detail"""
        response = super().test_api_get()
        courts = response.content['courts']
        self.assertGreaterEqual(len(courts), 1)
        return courts
