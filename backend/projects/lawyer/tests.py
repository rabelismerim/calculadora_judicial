import json
from core.abstract.tests import AbstractTest


class LawyerTest(AbstractTest):
    """lawyer related tests"""

    def test_api_C_post_lawyers(self):
        """Assert post lawyers detail"""
        self.printl('Criar advogado')
        lawyer = {
            "description": "Name Juiz 1"
        }
        response = self.client.post('/djud/api/v1/projects/lawyer', lawyer)
        self.assertEqual(response.status_code, 201)

    def test_api_D_get_lawyers(self):
        """Assert get lawyers detail"""
        self.printl('Lista de advogados')
        response = self.client.get('/djud/api/v1/projects/lawyer')
        self.assertEqual(response.status_code, 200)
