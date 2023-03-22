from core.abstract.tests import AbstractTest


class RegionTest(AbstractTest):
    """Region related tests"""

    path = 'projects/region'

    parameters = {
        "description": "Name Comarca 1"
    }

    def test_api_get(self):
        """Assert get Region detail"""
        response = super().test_api_get()
        objs = response.content['regions']
        self.assertGreaterEqual(len(objs), 1)
        return objs
