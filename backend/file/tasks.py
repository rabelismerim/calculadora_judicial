import io
import json
import pickle

import pandas as pd

from core.abstract.tasks import AbstractTask
from config.celery import app as celery_app


class ProcessExcel(AbstractTask):

    # def run(self, channel: str, excel_read: bytes, callback=None, **kwargs):
    #     excel_read = excel_read.decode('latin-1')
    #     # pandas_kwargs = {
    #     #     'sheet_name': "BASE",
    #     #     'header': 14,
    #     # }
    #     data = super().run(channel, excel_read, callback)
    #     if callback:
    #         funcao = pickle.loads(callback)
    #         funcao(data, **kwargs)
    #     return data

    # TODO: change to the other run method when the excel processing application is running independently as a micro
    #  service
    def run(self, channel: str, excel_read: bytes, callback=None, **kwargs):
        data = self.process_excel(excel_read)
        if callback:
            funcao = pickle.loads(callback)
            funcao(data, **kwargs)
        return data

    def process_excel(self, excel_bytes):
        stream = io.BytesIO(excel_bytes)
        df = pd.read_excel(stream)
        df["index"] = df.index + 1
        json_data = df.to_json(orient='records', date_format='iso', date_unit='s')
        return json.loads(json_data)


ProcessExcelTask = celery_app.register_task(ProcessExcel())
