import json
import random
from core.abstract.tests import AbstractTest
from projects.models import Project
from projects.project_user.models import ProjectUser
from utils import get_user_model


User = get_user_model()


class EngagementTest(AbstractTest):
    """Engagement related tests"""

    def test_api_E_post_engagements(self):
        """Assert post engagements detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create engagement')
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
            '/djud/api/v1/projects/engagement/', json.dumps(engagement), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.print_success('Created engagement')

    def test_api_F_get_engagements(self):
        """Assert get engagements detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List engagements')
        response = self.client.get('/djud/api/v1/projects/engagement/')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed engagements')
        engagements = response.json()['project_engagements']
        engagement = engagements[0]
        self.assertGreaterEqual(len(engagements), 1)
        self.print_success('Listed engagements >= 1')
