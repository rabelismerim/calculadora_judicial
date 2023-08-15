# """
# This module defines a Api's classes that provides HTTP methods for managing BigNumber objects models.
# It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
# Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
# Api's classes use the BigNumber model and schema BigNumber to work with data.
# """
# from time import sleep
#
# from celery import Task
# from celery.result import AsyncResult
# from django.http import JsonResponse
# from big_number.schemas import BigNumberSchema
# from calculation.models import Calculation
# from core.abstract.views import AbstractViewApi
#
# from security.views import Security
#
# from rest_framework import permissions
# from config.celery import app as celery_app, redis_conn
#
#
# class AbstractTask(Task):
#     __redis_conn = redis_conn
#     __security = Security()
#     max_retries = 3
#
#     def run(self):
#         print(f'running taskk{self.request.id}\n\n')
#         data = {'data': 'excel'}
#         self._publish('task-process-excel', data)
#         return self._await_result()
#
#     def _await_result(self):
#         result_key = self._get_result_key()
#         pubsub = self.__redis_conn.pubsub()
#         pubsub.subscribe(result_key)
#
#         for message in pubsub.listen():
#             print(message, 'message result')
#             if message['type'] == 'message':
#                 pubsub.unsubscribe(result_key)  # Stops listening to the channel
#                 data = self.__security.decrypt(message['data'].decode())
#                 print(data, 'dt received\n')
#                 return data
#
#     def _get_result_key(self):
#         return f'my_task_result_{self.request.id}'
#
#     def _publish(self, channel: str, obj: dict):
#         data = {'data': obj, 'task_id': self.request.id, 'key': self._get_result_key()}
#         cont = 0
#         while self.__redis_conn.publish(channel, self.__security.encrypt(data)) == 0:
#             print('Awaiting worker')
#             sleep(1)
#             cont += 1
#             if cont == 60:
#                 print('Worker not found')
#                 self.retry()
#
#
# class BigNumberApi(AbstractViewApi):
#     def get(self, request, *args, **kwargs):
#         task = TaskExample.delay()
#         return JsonResponse({'task_id': task.task_id})
#
#
# class BigNumberGetApi(AbstractViewApi):
#     http_method_names = ['get']
#     serializer_class = BigNumberSchema
#     permission_classes = [permissions.AllowAny]
#     model = Calculation
#
#     def get(self, request, *args, **kwargs):
#         task_id = kwargs.get('task_id')
#         result = AsyncResult(str(task_id))
#         data = {'status': result.status, 'content': result.result}
#         return JsonResponse(data)
#
#
# TaskExample = celery_app.register_task(AbstractTask())
