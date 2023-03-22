from core.abstract.tests import AbstractTest


class JudgeTest(AbstractTest):
    """judge related tests"""

    parameters = {
        "description": "Name Juiz 1"
    }

    path = 'projects/judge'

    def test_api_get(self):
        """Assert get courts detail"""
        response = super().test_api_get()
        objs = response.content['judges']
        self.assertGreaterEqual(len(objs), 1)
        return objs
