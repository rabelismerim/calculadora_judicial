import io
import json
import pickle

import pandas as pd

from core.abstract.tasks import AbstractTask
from config.celery import app as celery_app


class ProcessExcel(AbstractTask):

    def run(self, channel: str, excel_read: bytes, callback=None, **kwargs):
        data = self.excel_to_json(excel_read)
        if callback:
            funcao = pickle.loads(callback)
            funcao(data, **kwargs)
        return data

    def excel_to_json(self, excel_bytes, **pandas_kwargs):
        stream = io.BytesIO(excel_bytes)
        df = pd.read_excel(stream, **pandas_kwargs)
        df["index"] = df.index + 1
        json_data = df.to_json(orient='records', date_format='iso', date_unit='s')
        return json.loads(json_data)


ProcessExcelTask = celery_app.register_task(ProcessExcel())
