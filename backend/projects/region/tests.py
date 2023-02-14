import json
from core.abstract.tests import AbstractTest


class RegionTest(AbstractTest):
    """Region related tests"""

    def test_api_E_post_regions(self):
        """Assert post regions detail"""
        self.printl('Create regions')
        region = {
            "description": "Name Comarca 1"
        }

        response = self.client.post('/djud/api/v1/projects/region', region)
        self.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        self.set_project('region_id', content['regions']['id'])

    def test_api_F_get_regions(self):
        """Assert get regions detail"""
        self.printl('List regions')
        response = self.client.get('/djud/api/v1/projects/region')
        self.assertEqual(response.status_code, 200)
        regions = response.json()['regions']
        region = regions[0]
        self.assertGreaterEqual(len(regions), 1)
        self.set_project('region_id', region['id'])
