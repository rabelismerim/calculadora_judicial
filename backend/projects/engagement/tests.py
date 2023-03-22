import random
from core.abstract.tests import AbstractTest
from projects.models import Project
from projects.project_user.models import ProjectUser


class EngagementTest(AbstractTest):
    """Engagement related tests"""
    project = Project.objects.first()
    user = ProjectUser.objects.first()
    parameters = {
        "numbers": [
            f"{random.randint(50000, 100000)}"
        ],
        "users": [
            {
                "id": str(user.id)
            }
        ],
        "project_id": str(project.id)
    }

    path = 'projects/engagement'

    def test_api_get(self):
        """Assert get courts detail"""
        response = super().test_api_get()
        objs = response.content['project_engagements']
        self.assertGreaterEqual(len(objs), 1)
        return objs
