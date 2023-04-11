from core.abstract.tests import AbstractTest, generate_name


class JudgeTest(AbstractTest):
    """judge related tests"""

    parameters = {
        "description": generate_name()
    }

    path = 'projects/judge'

    def test_api_get(self):
        """Assert get courts detail"""
        response = super().test_api_get()
        objs = response.content['judges']
        self.assertGreaterEqual(len(objs), 1)
        return objs
