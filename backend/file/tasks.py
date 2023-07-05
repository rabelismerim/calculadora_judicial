import pickle
import re
import time
import uuid

from celery import Task
from django_celery_results.models import TaskResult
from unidecode import unidecode

from base.coins.models import COIN_CHOICES
from base.models import CHOICES_OCCURRENCE, CHOICES_REPRESENTATION_DOCUMENTATION, CHOICES_CLAIM_TYPE, \
    SELECT_CHOICES_REPRESENTATION_DOCUMENTATION, SELECT_CHOICES_CLAIM_TYPE
from core.abstract.tasks import AbstractTask
from config.celery import app as celery_app
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import Creditor, CHOICES_STATUS_LEGAL
from file.models import File

coin_dict = {choice[1]: choice[0].upper() for choice in COIN_CHOICES}
classes_dict = {choice[1].lower().replace('classe ', '').split('-')[0].strip(): choice[0] for choice in CLASSE_CHOICES}
representation_documentation_dict = {choice[0].lower(): choice[1] for choice in
                                     SELECT_CHOICES_REPRESENTATION_DOCUMENTATION}
claim_type_dict = {choice[0]: choice[1] for choice in SELECT_CHOICES_CLAIM_TYPE}


# CHOICES_STATUS_LEGAL
# CHOICES_OCCURRENCE
# CHOICES_CLAIM_TYPE


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
            funcao(data)
        # self.process_json_to_model(data)
        return data

    def _parse_keys(self, value):
        value = unidecode(value)
        # Remove caracteres especiais e mantém apenas letras
        return re.sub(r'[^a-zA-Z]+', '', value).lower().strip()

    def process_json_to_model(self, data: list):
        # Creditor.objects.create
        for credor in data:
            if credor['#']:
                new_keys_creditor = {}

                for key, value in credor.items():
                    new_keys_creditor[self._parse_keys(key)] = value

                print(new_keys_creditor, 'new_keys_creditor')
                # Creditor.objects.create(**credor) # TODO: criar logica de criacao aqui
                credor = new_keys_creditor
                # ab = credor['classeiiiquirografario']
                coin = coin_dict.get(credor['credormoeda'].upper())
                classes = classes_dict.get(credor['credorclasse'].lower().replace('classe', '').split('-')[0].strip())
                representation_documentation = representation_documentation_dict.get(
                    credor['documentacaoderepresentacao'].lower())
                claim_type = claim_type_dict.get(str(credor['tipo'])[0].upper())
                new_credor = {
                    "entity": {
                        "name": credor['credor'],
                        "legal_number": credor['credorcpfcnpjnaocolocarpontuacao']
                    },
                    "claim_creditor": [
                        {
                            "classes": {
                                "classe": classes
                            },
                            "coins": {
                                "coin": coin,
                                "value": credor['credorvalor']
                            },
                            "archive_json": {}
                        }
                    ],
                    "representation_documentation": representation_documentation,
                    "claim_type": claim_type,
                }

                print(new_credor)

                # TODO: subir credor inativo. Ter tela/endpoint pra aprovar credor


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
