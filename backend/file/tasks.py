import pickle
from core.abstract.tasks import AbstractTask
from config.celery import app as celery_app


class ProcessExcel(AbstractTask):

    def run(self, channel: str, excel_read: bytes, callback=None, **kwargs):
        excel_read = excel_read.decode('latin-1')
        # pandas_kwargs = {
        #     'sheet_name': "BASE",
        #     'header': 14,
        # }
        data = super().run(channel, excel_read, callback)
        if callback:
            funcao = pickle.loads(callback)
            funcao(data, **kwargs)
        return data


ProcessExcelTask = celery_app.register_task(ProcessExcel())
