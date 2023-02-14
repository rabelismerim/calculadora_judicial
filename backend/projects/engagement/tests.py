import json
import random
from core.abstract.tests import AbstractTest
from projects.models import Project
from projects.project_user.models import ProjectUser


class EngagementTest(AbstractTest):
    """Engagement related tests"""

    def test_api_E_post_engagements(self):
        """Assert post engagements detail"""
        self.printl('Create engagement')
        project = Project.objects.first()
        user = ProjectUser.objects.first()
        engagement = {
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

        response = self.client.post(
            '/djud/api/v1/projects/engagement', json.dumps(engagement), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_api_F_get_engagements(self):
        """Assert get engagements detail"""
        self.printl('List engagements')
        response = self.client.get('/djud/api/v1/projects/engagement')
        self.assertEqual(response.status_code, 200)
        engagements = response.json()['project_engagements']
        engagement = engagements[0]
        self.assertGreaterEqual(len(engagements), 1)
