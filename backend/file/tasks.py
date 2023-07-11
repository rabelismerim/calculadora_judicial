import pickle
import time
import uuid

from celery import Task
from django_celery_results.models import TaskResult
from core.abstract.tasks import AbstractTask
from config.celery import app as celery_app
from file.models import File


class ProcessExcel(AbstractTask):

    def run(self, channel: str, excel_read: bytes, callback=None, **kwargs):
        excel_read = excel_read.decode('latin-1')
        # pandas_kwargs = {
        #     'sheet_name': "BASE",
        #     'header': 14,
        # }
        print(excel_read, 'excel_read run\n')
        data = super().run(channel, excel_read, callback)
        if callback:
            funcao = pickle.loads(callback)
            funcao(data, **kwargs)
        return data


class SaveFile(Task):
    queue = 'save-file'  # Define a fila da task

    def run(self, task_id: uuid, file_id: uuid):
        cont = 0
        while True:
            task_result = TaskResult.objects.filter(task_id=task_id).first()
            if task_result:
                file = File.objects.filter(id=file_id).first()
                file.task_result = task_result
                file.save()
                return 'Task result associated with the File'
            time.sleep(10)
            cont += 1
            if cont == 60:
                self.retry()


ProcessExcelTask = celery_app.register_task(ProcessExcel())
SaveFileTask = celery_app.register_task(SaveFile())
response = {'Unnamed: 0': None,
            '#': 6.0,
            'Credor - Recuperanda': 'CARTONAGEM JACAREI EIRELI EPP',

            'Tipo': 'Análise de Ofício',
            'Edital - Nome': 'EMBACORP SOLUCOES EM EMBALAGEM DE PAPEL',
            'Edital - CPF/CNPJ (não colocar pontuação)': 32779402000118.0,
            'Edital - Classe': 'Classe III - Quirografário',
            'Edital - Moeda': 'BRL',
            'Edital - Valor': 23225.31,
            'Edital - Recuperanda': 'CARTONAGEM JACAREI EIRELI EPP',
            'Análise na ficha': None,
            'Natureza (NF, contrato, trabalhista etc)': 'Nota fiscal',
            'Responsável jurídico': 'TIAGO MACEDO',
            'Status jurídico': 'CONCLUÍDO',
            'Status cálculo': 'ENVIADO PARA CÁLCULO',
            'Revisão jurídica': 'PENDENTE',
            'Revisão Aires': 'PENDENTE',
            'Pasta': '03_REVISÃO_FINANCEIRA',
            'Tipo de análise': None,
            'Descrição': None,
            'Status': 'CONCLUÍDO',
            'Prazo resposta': None}
