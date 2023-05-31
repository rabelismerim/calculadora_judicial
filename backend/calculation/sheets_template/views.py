from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from calculation.statement.models import Statement
from calculation.statement_pf.models import StatementPF
from calculation.statement_pj.models import StatementPJ
from calculation.comparative.models import Comparative, ComparativeCalculation
from calculation.funds.models import Funds
from calculation.models import Calculation
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from django.core import serializers
from xlsx2html import xlsx2html

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc

import openpyxl as xl
from os.path import exists
from os import remove

import json

import base64

class SheetTemplateViewApi(AbstractViewApi):
    """HTTP methods for verdict"""
    http_method_names = ['get']
    serializer_class = SheetsTemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = SheetsTemplate

    query_params = []
    docs = {
        'init': _("""Represents templates to publishing external sheets models to frontend.`, 
                """),
    }

    @doc(_("""This method handles GET requests for the view. It retrieves a list of objects sheets file using the given 
                calculation_id from the query parameters and serializes the result into JSON format before returning it
                 as an HTTP response. 

                    Returns:
                        JsonResponse: An HTTP response containing the serialized sheets file data retrieved.
                    """))
    # This function changing the new output file name as report
    def new_archive(self, filename):
        sequence = 0
        new_name = filename.split('/')[-1]
        dir = '/'.join(filename.split('/')[:-1])
        name_file = new_name
        while True:
            new_name = str(sequence) + '_' + name_file
            if exists(dir + '/' + new_name):
                sequence += 1
            else:
                break
        return dir + '/' + new_name

    # This function have an interpretor in xls database, juca_value and juca_list,
    # searching value or lists in request calls
    def get(self, request, *args, **kwargs):

        try:
            calculation_id = kwargs.get('calculation_id')
            export_type = kwargs.get('export_type')
            Template = SheetsTemplate.objects.filter(name=export_type)
            if len(Template) <= 0:
                return JsonResponse({'errors': 'Template not found.'})

                # Objects to publish in sheet
            calculation_model = Calculation.objects.filter(id=calculation_id)
            calculation = json.loads(serializers.serialize("json", calculation_model))
            statement_model = Statement.objects.filter(calculation_id=calculation_id)
            if len(statement_model) > 0:
                statement = json.loads(serializers.serialize("json", statement_model))
                statement_pf_model = StatementPF.objects.filter(id=statement_model[0].id)
                statement_pf = json.loads(serializers.serialize("json", statement_pf_model))
                statement_pj_model = StatementPJ.objects.filter(id=statement_model[0].id)
                statement_pj = json.loads(serializers.serialize("json", statement_pj_model))
            comparative_model = Comparative.objects.filter(calculation_id=calculation_id)
            comparative = json.loads(serializers.serialize("json", comparative_model))
            comparativecalculation_model = ComparativeCalculation.objects.filter(id=calculation_id)
            comparativecalculation = json.loads(serializers.serialize("json", comparativecalculation_model))
            funds_model = Funds.objects.filter(calculation_id=calculation_id)
            funds = json.loads(serializers.serialize("json", funds_model))
            archive = xl.load_workbook("uploads/" + Template[0].file.name, read_only=False)
            new_name = self.new_archive("uploads/" + Template[0].file.name)

            for sheet in archive:
                for row in sheet.iter_rows():
                    for col in row:
                        if col.value:
                            if type(col.value) == str and col.value.find('JUCA=') >= 0:
                                try:
                                    col.value = str(eval(str(col.value)[5:]))
                                except:
                                    col.value = str("")
                        else:
                            pass

            archive.save(new_name)
            with open(new_name, 'rb') as archive_excel:
                excel_file = archive_excel.read()
                base64_encoded_data = base64.b64encode(excel_file)
                base64_message = base64_encoded_data.decode('latin-1')

            list_html = {}
            for sheet in archive:
                out_stream = xlsx2html(new_name, sheet=sheet._WorkbookChild__title, parse_formula=False)
                out_stream.seek(0)
                result_html = out_stream.read()
                result_html = result_html.replace('\n    ', '').replace('\n', '').replace('\\"', '"')
                list_html[sheet._WorkbookChild__title] = result_html

            remove(new_name)
            return JsonResponse({"html": f"\"{str(list_html)}\"", "excel": f"{base64_message}"})

        except BaseException as e:
            return JsonResponse({'errors': str(e)})
