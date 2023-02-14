# import json
# from core.abstract.tests import AbstractTest


# class CreditorTest(AbstractTest):
#     """Creditor related tests"""

#     def test_api_E_post_creditors(self):
#         """Assert post creditors detail"""
#         self.printl('Criar Creditor')
#         creditor = {
#             "description": "Name Creditor 1"
#         }

#         response = self.client.post('/djud/api/v1/projects/creditor', creditor)
#         self.assertEqual(response.status_code, 201)
#         content = json.loads(response.content)
#         self.set_project('creditor_id', content['creditors']['id'])

#     def test_api_F_get_creditors(self):
#         """Assert get creditors detail"""
#         self.printl('Lista de Creditors')
#         response = self.client.get('/djud/api/v1/projects/creditor')
#         self.assertEqual(response.status_code, 200)
#         creditors = response.json()['creditors']
#         creditor = creditors[0]
#         self.assertGreaterEqual(len(creditors), 1)
#         self.set_project('creditor_id', creditor['id'])
