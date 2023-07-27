import time

from celery import Task

from config.celery import app as celery_app


class ClassTaskExample(Task):
    """
    A celery Task class that executes an example task.
    When run, it prints a message, sleeps for 2 seconds, prints a "task finished" message,
    publishes a message to the 'finished-task' Redis channel, and returns a dictionary with a "message" key.
    """

    def run(self):
        print(f'Executing scheduled task\n')
        time.sleep(3)
        print(f'Scheduled task executed\n')
        # redis_conn.publish('finished-task', json.dumps({'message': 'result', 'task_id': self.request.id}))
        return {'message': 'finished task'}


TaskExample = celery_app.register_task(ClassTaskExample())
