from core.abstract.tests import AbstractTest, generate_name


class CourtTest(AbstractTest):
    """Court related tests"""

    parameters = {
        "description": generate_name()
    }
    path = 'projects/court'

    def test_api_get(self):
        """Assert get courts detail"""
        response = super().test_api_get()
        courts = response.content['courts']
        self.assertGreaterEqual(len(courts), 1)
        return courts
