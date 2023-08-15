import json
import logging
from time import sleep

from celery import Task

from security.views import Security

from config.celery import redis_conn

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log_file_celery.txt')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class AbstractTask(Task):
    __redis_conn = redis_conn
    __security = Security()
    max_retries = 3

    def send_log(self, *messages):
        for message in messages:
            logger.info(message)

    def run(self, channel, excel_read, callback: callable = None, **kwargs):
        print(excel_read, 'excel_read run abstract\n')
        self.send_log(f'running task {self.request.id}')
        self._publish(channel, excel_read, **kwargs)
        return self._await_result()

    def _await_result(self):
        result_key = self._get_result_key()
        pubsub = self.__redis_conn.pubsub()
        pubsub.subscribe(result_key)

        for message in pubsub.listen():
            self.send_log(message, 'message result')
            if message['type'] == 'message':
                pubsub.unsubscribe(result_key)  # Stops listening to the channel
                data = json.loads(self.__security.decrypt(message['data'].decode()))
                self.send_log(type(data), 'dt received\n')
                self.send_log(data, 'dt received\n')
                return data

    def _get_result_key(self):
        return f'my_task_result_{self.request.id}'

    def _publish(self, channel: str, obj: bytes, **kwargs):
        data = {'data': obj, 'task_id': self.request.id, 'key': self._get_result_key(), 'pandas_kwargs': kwargs}
        cont = 0
        while self.__redis_conn.publish(channel, self.__security.encrypt(data)) == 0:
            self.send_log('Awaiting worker')
            sleep(1)
            cont += 1
            if cont == 60:
                self.send_log('Worker not found')
                self.retry()
