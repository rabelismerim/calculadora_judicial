from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from calculation.statement.models import Statement
from calculation.statement_pf.models import StatementPF
from calculation.statement_pj.models import StatementPJ
from rates.models import Rate
from creditors.notice.models import Notice
from calculation.comparative.models import Comparative, ComparativeCalculation
from calculation.funds.models import Funds
from calculation.models import Calculation
from creditors.models import Creditor 
from base.coins.models import Coins
from creditors.classes.models import Classes
from recovering.models import Recovering

from projects.models import Project
from projects.court.models import Court
from core.entity.models import Entity
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from django.core import serializers
from xlsx2html import xlsx2html

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc

import openpyxl as xl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from os.path import exists
from os import remove
from datetime import datetime
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
            calculation = Calculation.objects.filter(id=calculation_id)
            if len(calculation) <= 0:
                return JsonResponse({'errors': 'Calculation not found.'})
            creditor = Creditor.objects.filter(id=calculation[0].creditor_id)    
            statement = Statement.objects.filter(calculation_id=calculation_id)
            if len(statement) > 0:
                statement_pf = StatementPF.objects.filter(id=statement[0].id)
                statement_pj = StatementPJ.objects.filter(id=statement[0].id)
            comparative = Comparative.objects.filter(calculation_id=calculation_id)
            comparativecalculation = ComparativeCalculation.objects.filter(id=calculation_id)
            funds = Funds.objects.filter(calculation_id=calculation_id)
            if len(funds)>0:
                classes = Classes.objects.filter(id=funds[0].classes_id)
                coins = Coins.objects.filter(id=funds[0].coins_id)
            if len(creditor)>0:
                notice = Notice.objects.filter(creditor_id=creditor[0].id)
                if len(notice)>0:
                    classes_notice = Classes.objects.filter(id=notice[0].classes_id)
                if len(notice)>0:
                    coins_notice = Coins.objects.filter(id=notice[0].coins_id)
                recovering = Recovering.objects.filter(id=creditor[0].recovering_id)
                if len(recovering)>0:
                    project = Project.objects.filter(id=recovering[0].project_id)
                entity = Entity.objects.filter(id=creditor[0].entity_id)
                if len(entity)>0:
                    calculations_sheet = Calculation.objects.filter(creditor__entity=entity[0])
                recovering_entity = Entity.objects.filter(id=creditor[0].entity_id)
            if len(funds)>0:
                rate = Rate.objects.filter(id=funds[0].rate_id)
            court = Court.objects.filter(id=project[0].court_id)

            #open the archive and process
            archive_download = xl.load_workbook("uploads/" + Template[0].file.name, read_only=False)
            archive_view = xl.load_workbook("uploads/" + Template[0].file.name.upper().replace('.XLSX', '-VIEW.XLSX'), read_only=False)
            new_name_download = self.new_archive("uploads/" + Template[0].file.name)
            new_name_view = self.new_archive("uploads/" + Template[0].file.name.upper().replace('.XLSX', '-VIEW.XLSX'))

            for sheet in archive_download:
                for row in sheet.iter_rows():
                    for col in row:
                        if col.value:
                            if type(col.value) == str and col.value.find('JUCA=')==0:
                                try:
                                    col.value = str(eval(str(col.value)[5:]))
                                except:
                                    col.value = str("Erro Formula!!!")
                        else:
                            pass
            for sheet in archive_view:
                cnt_calc = 0
                if type(sheet.title) == str and sheet.title.find('JUCA=') >= 0:
                    if str(sheet.title)[5:]=='Calculation':
                        copy_sheet=archive_view[sheet.title]
                        for item in funds:
                            cnt_row=2
                            archive_view.copy_worksheet(copy_sheet)
                            ws = archive_view[sheet.title+' Copy']
                            ws.title = item.name
                            plan_build = item.get_all_statement_funds_integrations()
                            if plan_build and len(plan_build)>0:
                                font = Font(bold=True)
                                ws['D'+str(cnt_row)]='Crédito '+plan_build[0].fund.template.name
                                ws['D'+str(cnt_row)].font=font
                                ws['D'+str(cnt_row+2)]='Integrações sobre '+str(plan_build[0].fund.rate)
                                ws['D'+str(cnt_row+2)].font=font
                                ws['D'+str(cnt_row+3)]=plan_build[0].fund.name
                                ws['D'+str(cnt_row+3)].font=font
                                ws['D'+str(cnt_row+4)]=str(plan_build[0].fund.classes)
                                ws['D'+str(cnt_row+4)].font=font
                                ws['D'+str(cnt_row+5)]="Descrição"
                                ws['D'+str(cnt_row+5)].font=font
                                grayFill = PatternFill(start_color='00C0C0C0',
                                end_color='00C0C0C0',
                                fill_type='solid')
                                ws['D'+str(cnt_row+2)]='Integrações sobre '+str(item.rate)
                                ws['D'+str(cnt_row+2)].font=font
                                ws['D'+str(cnt_row+3)]=item.name
                                ws['D'+str(cnt_row+3)].font=font
                                ws['D'+str(cnt_row+4)]=str(item.classes)
                                ws['D'+str(cnt_row+4)].font=font
                                ws['D'+str(cnt_row+5)]="Descrição"
                                ws['D'+str(cnt_row+5)].font=font
                                ws['D'+str(cnt_row+5)].fill=grayFill
                                ws['E'+str(cnt_row+5)]="Data base"
                                ws['E'+str(cnt_row+5)].font=font
                                ws['E'+str(cnt_row+5)].fill=grayFill
                                ws['F'+str(cnt_row+5)]="Súmula 381"
                                ws['F'+str(cnt_row+5)].font=font
                                ws['F'+str(cnt_row+5)].fill=grayFill
                                ws['G'+str(cnt_row+5)]="Valor histórico"
                                ws['G'+str(cnt_row+5)].font=font
                                ws['G'+str(cnt_row+5)].fill=grayFill
                                ws['H'+str(cnt_row+5)]="Indíce na data base"
                                ws['H'+str(cnt_row+5)].font=font
                                ws['H'+str(cnt_row+5)].fill=grayFill
                                ws['I'+str(cnt_row+5)]="Indíce na recuperação"
                                ws['I'+str(cnt_row+5)].font=font
                                ws['I'+str(cnt_row+5)].fill=grayFill
                                ws['J'+str(cnt_row+5)]="Valor corrigido"
                                ws['J'+str(cnt_row+5)].font=font
                                ws['J'+str(cnt_row+5)].fill=grayFill
                                cnt_row=cnt_row+6
                                for item1 in plan_build:
                                    ws['D'+str(cnt_row)]=str(item1.description).strip()
                                    ws['E'+str(cnt_row)].alignment = Alignment(horizontal="center")
                                    ws['E'+str(cnt_row)]=datetime.strftime(item1.data_base, "%d/%m/%Y")
                                    ws['F'+str(cnt_row)].alignment = Alignment(horizontal="center")
                                    ws['F'+str(cnt_row)]='Sim' if item1.summary==True else 'Não'
                                    ws['G'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['G'+str(cnt_row)]='{:,.2f}'.format(float(item1.historical_value)).strip().replace('.','-').replace(',','.').replace('-',',')
                                    ws['H'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['H'+str(cnt_row)]='{:,.5f}'.format(float(item1.monetarycorrectionintegrations.index_data_base)).strip().replace('.','-').replace(',','.').replace('-',',')
                                    ws['I'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['I'+str(cnt_row)]='{:,.5f}'.format(float(item1.monetarycorrectionintegrations.index_recovering)).strip().replace('.','-').replace(',','.').replace('-',',')
                                    ws['J'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['J'+str(cnt_row)]='{:,.2f}'.format(float(item1.monetarycorrectionintegrations.corrected_value)).strip().replace('.','-').replace(',','.').replace('-',',')
                                    cnt_row=cnt_row+1
                            else:
                                font = Font(bold=True)
                                ws['D'+str(cnt_row)]='Crédito '+item.template.name
                                ws['D'+str(cnt_row)].font=font
                                grayFill = PatternFill(start_color='00C0C0C0',
                                end_color='00C0C0C0',
                                fill_type='solid')
                                ws['D'+str(cnt_row+2)]='Integrações sobre '+str(item.rate)
                                ws['D'+str(cnt_row+2)].font=font
                                ws['D'+str(cnt_row+3)]=item.name
                                ws['D'+str(cnt_row+3)].font=font
                                ws['D'+str(cnt_row+4)]=str(item.classes)
                                ws['D'+str(cnt_row+4)].font=font
                                ws['D'+str(cnt_row+5)]="Descrição"
                                ws['D'+str(cnt_row+5)].font=font
                                ws['D'+str(cnt_row+5)].fill=grayFill
                                ws['E'+str(cnt_row+5)]="Data base"
                                ws['E'+str(cnt_row+5)].font=font
                                ws['E'+str(cnt_row+5)].fill=grayFill
                                ws['F'+str(cnt_row+5)]="Súmula 381"
                                ws['F'+str(cnt_row+5)].font=font
                                ws['F'+str(cnt_row+5)].fill=grayFill
                                ws['G'+str(cnt_row+5)]="Valor histórico"
                                ws['G'+str(cnt_row+5)].font=font
                                ws['G'+str(cnt_row+5)].fill=grayFill
                                ws['H'+str(cnt_row+5)]="Indíce na data base"
                                ws['H'+str(cnt_row+5)].font=font
                                ws['H'+str(cnt_row+5)].fill=grayFill
                                ws['I'+str(cnt_row+5)]="Indíce na recuperação"
                                ws['I'+str(cnt_row+5)].font=font
                                ws['I'+str(cnt_row+5)].fill=grayFill
                                ws['J'+str(cnt_row+5)]="Valor corrigido"
                                ws['J'+str(cnt_row+5)].font=font
                                ws['J'+str(cnt_row+5)].fill=grayFill
                                cnt_row=cnt_row+6
                            cnt_row=cnt_row+2
                            plan_build1 = item.get_all_statement_funds()
                            if plan_build1 and len(plan_build1)>0:
                                font = Font(bold=True)
                                grayFill = PatternFill(start_color='00C0C0C0',
                                end_color='00C0C0C0',
                                fill_type='solid')
                                ws['D'+str(cnt_row)]=str(plan_build1[0].fund.rate)
                                ws['D'+str(cnt_row)].font=font
                                ws['D'+str(cnt_row+1)]="Data base"
                                ws['D'+str(cnt_row+1)].font=font
                                ws['D'+str(cnt_row+1)].fill=grayFill
                                ws['E'+str(cnt_row+1)]="Súmula 381"
                                ws['E'+str(cnt_row+1)].font=font
                                ws['E'+str(cnt_row+1)].fill=grayFill
                                ws['F'+str(cnt_row+1)]="Reflexos DSR"
                                ws['F'+str(cnt_row+1)].font=font
                                ws['F'+str(cnt_row+1)].fill=grayFill
                                ws['G'+str(cnt_row+1)]="Valor histórico"
                                ws['G'+str(cnt_row+1)].font=font
                                ws['G'+str(cnt_row+1)].fill=grayFill
                                ws['H'+str(cnt_row+1)]="Indíce na data base"
                                ws['H'+str(cnt_row+1)].font=font
                                ws['H'+str(cnt_row+1)].fill=grayFill
                                ws['I'+str(cnt_row+1)]="Indíce na recuperação"
                                ws['I'+str(cnt_row+1)].font=font
                                ws['I'+str(cnt_row+1)].fill=grayFill
                                ws['J'+str(cnt_row+1)]="Valor corrigido"
                                ws['J'+str(cnt_row+1)].font=font
                                ws['J'+str(cnt_row+1)].fill=grayFill
                                cnt_row=cnt_row+2
                                for item2 in plan_build1:
                                    ws['D'+str(cnt_row)]=datetime.strftime(item2.data_base, "%d/%m/%Y")
                                    ws['E'+str(cnt_row)].alignment = Alignment(horizontal="center")
                                    ws['E'+str(cnt_row)]='Sim' if item2.summary==True else 'Não'
                                    ws['F'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['F'+str(cnt_row)]='{:,.2f}'.format(float(item2.dsr_reflexes)).replace('.','-').replace(',','.').replace('-',',')
                                    ws['G'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['G'+str(cnt_row)]='{:,.2f}'.format(float(item2.historical_value)).replace('.','-').replace(',','.').replace('-',',')
                                    value_index=item2.get_monetary_correction()
                                    ws['H'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['H'+str(cnt_row)]='{:,.5f}'.format(float(value_index.index_data_base)).replace('.','-').replace(',','.').replace('-',',')
                                    ws['I'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['I'+str(cnt_row)]='{:,.5f}'.format(float(value_index.index_recovering)).replace('.','-').replace(',','.').replace('-',',')
                                    ws['J'+str(cnt_row)].alignment = Alignment(horizontal="right")
                                    ws['J'+str(cnt_row)]='{:,.2f}'.format(float(str(value_index).split(' - ')[2])).replace('.','-').replace(',','.').replace('-',',')
                                    cnt_row=cnt_row+1
                            else:
                                font = Font(bold=True)
                                grayFill = PatternFill(start_color='00C0C0C0',
                                end_color='00C0C0C0',
                                fill_type='solid')
                                ws['D'+str(cnt_row)]=str(item.rate)
                                ws['D'+str(cnt_row)].font=font
                                ws['D'+str(cnt_row+1)]="Data base"
                                ws['D'+str(cnt_row+1)].font=font
                                ws['D'+str(cnt_row+1)].fill=grayFill
                                ws['E'+str(cnt_row+1)]="Súmula 381"
                                ws['E'+str(cnt_row+1)].font=font
                                ws['E'+str(cnt_row+1)].fill=grayFill
                                ws['F'+str(cnt_row+1)]="Reflexos DSR"
                                ws['F'+str(cnt_row+1)].font=font
                                ws['F'+str(cnt_row+1)].fill=grayFill
                                ws['G'+str(cnt_row+1)]="Valor histórico"
                                ws['G'+str(cnt_row+1)].font=font
                                ws['G'+str(cnt_row+1)].fill=grayFill
                                ws['H'+str(cnt_row+1)]="Indíce na data base"
                                ws['H'+str(cnt_row+1)].font=font
                                ws['H'+str(cnt_row+1)].fill=grayFill
                                ws['I'+str(cnt_row+1)]="Indíce na recuperação"
                                ws['I'+str(cnt_row+1)].font=font
                                ws['I'+str(cnt_row+1)].fill=grayFill
                                ws['J'+str(cnt_row+1)]="Valor corrigido"
                                ws['J'+str(cnt_row+1)].font=font
                                ws['J'+str(cnt_row+1)].fill=grayFill
                                cnt_row=cnt_row+3

            for sheet in archive_view:
                if type(sheet.title) == str and sheet.title.find('JUCA=') >= 0:
                    archive_view.remove_sheet(archive_view[sheet.title])
                sheet.title=sheet.title.replace(' Copy','')
            for sheet in archive_view:
                for row in sheet.iter_rows():
                    for col in row:
                        if col.value:
                            if type(col.value) == str and col.value.find('JUCA=') >= 0:
                                try:
                                    col.value = str(eval(str(col.value)[5:]))
                                except:
                                    col.value = str("Erro Formula!!!")
                        else:
                            pass

            archive_download.save(new_name_download)
            archive_view.save(new_name_view)

            with open(new_name_download, 'rb') as archive_excel:
                excel_file = archive_excel.read()
                base64_encoded_data = base64.b64encode(excel_file)
                base64_message = base64_encoded_data.decode('latin-1')

            list_html = {}
            for sheet in archive_view:
                out_stream = xlsx2html(new_name_view, sheet=sheet.title, parse_formula=False)
                out_stream.seek(0)
                result_html = out_stream.read()
                result_html = result_html.replace('\n    ', '').replace('\n', '').replace('\\"', '"')
                list_html[sheet._WorkbookChild__title] = result_html

            remove(new_name_download)
            remove(new_name_view)

            return JsonResponse({"html": f"\"{str(list_html)}\"", "excel": f"{base64_message}"})

        except BaseException as e:
            return JsonResponse({'errors': str(e)})
