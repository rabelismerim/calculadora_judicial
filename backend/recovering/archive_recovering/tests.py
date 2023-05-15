# import json
# from core.abstract.tests import AbstractTest
# from recovering.models import Recovering
# from utils import get_user_model
#
# # Desabilitado na fase 1
# User = get_user_model()
#
#
# class ArchiveRecoveringTest(AbstractTest):
#     """Recovering related tests"""
#
#     def test_api_E_post_archive_recoverings(self):
#         """Assert post Archive Recovering detail"""
#         user = User.objects.get(username='user1')
#         self.client.force_login(user)
#         self.print_start('Create Archive Recovering')
#         recovering = Recovering.objects.first()
#         archive_recovering = {
#             "archive": {
#                 "archive_json": {},
#                 "description": "string"
#             },
#             "recovering_id": str(recovering.id)
#         }
#
#         response = self.client.post(
#             '/juca/api/v1/recovering/archive_recovering', json.dumps(archive_recovering), content_type="application/json")
#         self.assertEqual(response.status_code, 201)
#         self.print_success('Created archive recovering')
#
#     def test_api_F_get_archive_recoverings(self):
#         """Assert get Archive Recoverings detail"""
#         user = User.objects.get(username='user1')
#         self.client.force_login(user)
#         self.print_start('List Archive Recovering')
#         response = self.client.get(
#             '/juca/api/v1/recovering/archive_recovering')
#         self.assertEqual(response.status_code, 200)
#         self.print_success('Listed archive recoverings')
#         archive_recoverings = response.json()['archive_recoverings']
#         archive_recoverings = archive_recoverings[0]
#         self.assertGreaterEqual(len(archive_recoverings), 1)
#         self.print_success('Listed archive recoverings >= 1')
