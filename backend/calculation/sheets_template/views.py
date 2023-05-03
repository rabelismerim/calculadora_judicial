from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc

import openpyxl as xl
from os.path import exists
from os import remove

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

    #This function changing the new output file name as report
    def new_archive(self, filename):
        sequence = 0
        new_name = filename.split('/')[-1]
        dir = '/'.join(filename.split('/')[:-1])
        while True:
            new_name = str(sequence) + '_' + new_name
            if exists(dir + '/' + new_name):
                sequence+=1
            else:
                break
        return dir + '/' + new_name

    #This function have an interpretor in xls database, juca_value and juca_list, 
    #searching value or lists in request calls
    def get(self, request, *args, **kwargs):

        try:
            calculation_id = kwargs.get('calculation_id')
            export_type = kwargs.get('export_type')
            Template = SheetsTemplate.objects.filter(name=export_type)

            archive = xl.load_workbook(Template[0].file.name, read_only=False)
            new_name = self.new_archive(Template[0].file.name)

            for sheet in archive:
                for col in sheet.iter_rows():
                    for cell in col:
                        if cell.value.find('JUCA=')>=0:
                            cell.value=eval(str(cell_value)[5:])
                        else:
                            pass

            archive.save(new_name)

            with open(new_name,'rb') as archive_excel:
                excel_file = archive_excel.readline()

            remove(new_name)

            return JsonResponse({'excel': [ str(excel_file) ]})

        except BaseException as e:
            return JsonResponse({'errors': dict(e)})
