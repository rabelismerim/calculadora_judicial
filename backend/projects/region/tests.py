import json
from core.abstract.tests import AbstractTest
from utils import get_user_model


User = get_user_model()


class RegionTest(AbstractTest):
    """Region related tests"""

    def test_api_E_post_regions(self):
        """Assert post regions detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('Create regions')
        region = {
            "description": "Name Comarca 1"
        }

        response = self.client.post('/djud/api/v1/projects/region', region)
        self.assertEqual(response.status_code, 201)
        self.print_success('Created region')
        content = json.loads(response.content)
        self.set_project('region_id', content['regions']['id'])

    def test_api_F_get_regions(self):
        """Assert get regions detail"""
        user = User.objects.get(username='user1')  
        self.client.force_login(user) 
        self.print_start('List regions')
        response = self.client.get('/djud/api/v1/projects/region')
        self.assertEqual(response.status_code, 200)
        self.print_success('Listed regions')
        regions = response.json()['regions']
        region = regions[0]
        self.assertGreaterEqual(len(regions), 1)
        self.print_success('Listed regions >= 1')
        self.set_project('region_id', region['id'])
