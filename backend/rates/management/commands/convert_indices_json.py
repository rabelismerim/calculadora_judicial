import json
import logging
import os
from datetime import datetime

import openpyxl
from django.core.management.base import BaseCommand
from rates.models import CalculeRate, Rate


def serialize_date(date):
    if isinstance(date, datetime):
        return date.date().isoformat()


def excel_to_json(file_path, sheet_name, output_folder):

    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook[sheet_name]

    data_list = []

    for row in sheet.iter_rows(min_row=3, values_only=True):
        if row[0] is not None and row[1] is not None:
            data_dict = {
                'date': serialize_date(row[0]),
                'accumulated': row[1]
            }
        data_list.append(data_dict)

    if data_list:
        output_json_file = os.path.join(output_folder, 'TJSP.json')
        with open(output_json_file, 'w') as json_file:
            json.dump({'is_per_day': False, 'index': sheet_name,
                       'values': data_list}, json_file, indent=4)

        logging.info(f'Arquivo JSON gerado com sucesso: {output_json_file}')
    else:
        logging.info('Nenhum registro válido encontrado.')


class Command(BaseCommand):
    """
    A management command to convert the columns of an Excel file to JSON.
    """

    def handle(self, *args, **options):
        excel_file_path = 'C:/projetoCalculadoraJudicial/DJUD/backend/uploads/calculadora-judicial/templates/04_RECUPERANDA_SOLICITACAO_E_ELABORACAO_DE_CALCULO.xlsm'
        sheet_name = 'TJSP'
        output_folder = 'C:/projetoCalculadoraJudicial/DJUD/backend/rates/indices_json'
        excel_to_json(excel_file_path, sheet_name, output_folder)
