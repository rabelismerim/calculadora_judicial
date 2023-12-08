import re
from copy import copy

from openpyxl.utils import range_boundaries, get_column_letter

from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from calculation.funds.document.models import StatementDocument, FundDocument
from calculation.statement.models import Statement
from creditors.notice.models import Notice
from calculation.models import Calculation, Premise
from calculation.funds.models import Funds
from creditors.models import Creditor
from base.claim.models import ClaimCreditor, ClaimLawyer
from recovering.models import Recovering
from projects.models import Project
from projects.court.models import Court
from core.entity.models import Entity
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from django.db.models import Sum
from xlsx2html import xlsx2html

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc

import pdfkit
import openpyxl as xl
from openpyxl.styles import PatternFill, Alignment, Font
from os.path import exists
from os import remove
from datetime import datetime
import base64

config = pdfkit.configuration(wkhtmltopdf="C:\Program Files\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

grayFill = PatternFill(start_color="00C0C0C0",
                       end_color="00C0C0C0", fill_type="solid")

grayFill1 = PatternFill(start_color="00D9D9D9",
                        end_color="00D9D9D9", fill_type="solid")

font = Font(bold=True)
total_merged = 2


def move_cell(cell, rows: int, cols: int, preserve_original=False) -> None:
    """Move ``cell`` by ``rows`` and ``cols``. If ``preserve_original`` is True, do copy instead
    of a move.

    .. note:: Anything already present in the new destination gets overwritten.
    """
    new_column = get_column_letter(cell.column + cols)
    new_cell = cell.parent[f"{new_column}{cell.row + rows}"]
    new_cell.value = cell.value
    if cell.has_style:
        new_cell.font = copy(cell.font)
        new_cell.border = copy(cell.border)
        new_cell.fill = copy(cell.fill)
        new_cell.number_format = copy(cell.number_format)
        new_cell.protection = copy(cell.protection)
        new_cell.alignment = copy(cell.alignment)
    if not preserve_original:
        cell.value = ""
        cell.style = "Normal"


def set_sheet_value(sheet_, line, column: str or list, value, force=False, alignment=None):
    if force:
        merged_cells_range = sheet_.merged_cells.ranges
        for merged_cell in merged_cells_range:
            if merged_cell.min_row >= line:
                merged_cell.shift(0, 1)
        sheet_.insert_rows(line, 1)

    if isinstance(column, list):
        sheet_.merge_cells(f'{column[0]}{line}:{column[1]}{line}')
        column = column[0]

    sheet_[f'{column}{line}'] = str(value)

    if alignment:
        sheet_[column + str(line)].alignment = Alignment(horizontal=alignment)
    elif column.startswith("C"):
        sheet_[column + str(line)].alignment = Alignment(horizontal='right')

    return sheet_


def set_sheet_number(sheet_, line, column, value, alignment=None):
    sheet_[f'{column}{line}'] = (
        "{:,.2f}".format(value)
        .replace(".", "|")
        .replace(",", ".")
        .replace("|", ",")
    )

    if alignment:
        sheet_[column + str(line)].alignment = Alignment(horizontal=alignment)
    elif column.startswith("C"):
        sheet_[column + str(line)].alignment = Alignment(horizontal='right')

    return sheet_


def delete_rows(sheet_, line, quantity=1):
    merged_cells_range = sheet_.merged_cells.ranges
    for merged_cell in merged_cells_range:
        if merged_cell.min_row >= line:
            merged_cell.shift(0, -quantity)
    sheet_.delete_rows(line, quantity)


class SheetTemplateViewApi(AbstractViewApi):
    """HTTP methods for verdict"""

    http_method_names = ["get"]
    serializer_class = SheetsTemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = SheetsTemplate

    docs = {
        "init": _(
            """Represents templates to publishing external sheets models to frontend.`, 
                """
        ),
    }

    @doc(
        _(
            """This method handles GET requests for the view. It retrieves a list of objects sheets file using the given 
                calculation_id from the query parameters and serializes the result into JSON format before returning it
                 as an HTTP response. 

                    :return:  # sourcery skip: avoid-builtin-shadow
                        JsonResponse: An HTTP response containing the serialized sheets file data retrieved.
                    """
        )
    )
    # This function changing the new output file name as report
    def new_archive(self, filename):
        sequence = 0
        new_name = filename.split("/")[-1]
        dir = "/".join(filename.split("/")[:-1])
        name_file = new_name
        while True:
            new_name = f"{str(sequence)}_{name_file}"
            if exists(f"{dir}/{new_name}"):
                sequence += 1
            else:
                break
        return f"{dir}/{new_name}"

    # This function have an interpretor in xls database, juca_value and juca_list,
    # searching value or lists in request calls
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get("calculation_id")
        name_report = kwargs.get("export_type").split(';')[0] if len(
            kwargs.get("export_type").split(';')) > 1 else kwargs.get("export_type")
        export_type = kwargs.get("export_type").split(';')[1] if len(
            kwargs.get("export_type").split(';')) > 1 else None
        Template = SheetsTemplate.objects.filter(name=name_report)
        if len(Template) <= 0:
            return JsonResponse({"errors": "Template not found."})

        # Objects to publish in sheet
        calculation = Calculation.objects.filter(id=calculation_id).first()
        if not calculation:
            return JsonResponse({"errors": "Calculation not found."})

        creditor = calculation.creditor
        statement = calculation.get_statement()

        funds = calculation.funds_set.all()
        premises = calculation.get_premises()
        fund_document = FundDocument.objects.filter(
            calculation_id=calculation_id)

        if len(fund_document) > 0:
            statement_document = StatementDocument.objects.filter(
                fund_id=fund_document[0].id
            )
        notice = creditor.get_notice()
        claim_creditor = creditor.get_claims_creditor().order_by("classes__classe")

        print(creditor.id, 'claim_creditor\n\n')
        print(claim_creditor, 'claim_creditor\n\n')
        claim_lawyer = creditor.get_claim_lawyer()

        recovering = creditor.recovering

        recovering_name = recovering.entity.name
        project = creditor.recovering.project
        entity = creditor.entity

        court = project.court
        # open the archive and process
        archive_view = xl.load_workbook(
            "uploads/"
            + Template[0].file.name.upper(),
            read_only=False,
        )
        new_name_view = self.new_archive(
            "uploads/"
            + Template[0].file.name.upper().replace(".XLSX", "-VIEW.XLSX")
        )
        new_name_pdf = self.new_archive(
            "uploads/"
            + Template[0].file.name.upper().replace(".XLSX", ".PDF")
        )

        juca_excel = {
            'credor_name': entity.name,
            'legal_number': entity.legal_number,
            'incident_number': calculation.incident_number,
            'court_name': court.description,
            'has_edital': 'Sim' if calculation.has_edital else 'Não',
            'has_advocative_hours': 'Sim' if calculation.has_advocative_hours else 'Não',
            'recovering_name': recovering_name,
            'admission': creditor.admission,
            'dismissal': creditor.dismissal,
            'date_rj_request': calculation.get_date_rj_request(),
            'date_rj_filing,': calculation.get_date_rj_filing(),
            'date_citation,': calculation.get_date_citation(),
            'legend_default_interest': calculation.get_legend_default_interest(),
            'legend_fine': calculation.get_legend_fine(),
            'fine': calculation.get_fine(),
            'default_interest': calculation.get_default_interest(),
            'legend_advocative_hours': calculation.get_legend_advocative_hours(),
            'advocative_hours': calculation.get_advocative_hours(),
            'executor': calculation.executor,
            'reviewer': calculation.reviewer,
            'approver': calculation.approver,
            'legend_impugnacao_or_habilitacao': statement.get_conclusion_display(),
            'legend_citation_filling': 'Data da citação:' if calculation.is_citation() else 'Data do ajuizamento da RJ:',
        }

        for sheet in archive_view:
            if sheet.sheet_state == "hidden":
                continue
            # cnt_calc = 0
            # merged_cells_range = sheet.merged_cells.ranges
            if type(sheet.title) == str and sheet.title.find("JUCA=") >= 0:
                if str(sheet.title)[5:] == "Calculation":
                    copy_sheet = archive_view[sheet.title]
                    for item in funds:
                        cnt_row = 2
                        archive_view.copy_worksheet(copy_sheet)
                        ws = archive_view[sheet.title + " Copy"]
                        ws.title = item.name
                        plan_build = item.get_all_statement_funds_integrations()
                        if plan_build and len(plan_build) > 0:
                            ws["D" + str(cnt_row)] = (
                                    "Crédito " +
                                    plan_build[0].fund.template.name
                            )
                            ws["D" + str(cnt_row)].font = font
                            ws["D" + str(cnt_row + 2)] = "Integrações sobre " + str(
                                plan_build[0].fund.template.name
                            )
                            ws["D" + str(cnt_row + 2)].font = font
                            ws["D" + str(cnt_row + 3)
                               ] = plan_build[0].fund.name
                            ws["D" + str(cnt_row + 3)].font = font
                            ws["D" + str(cnt_row + 4)] = str(
                                plan_build[0].fund.classes
                            )
                            ws["D" + str(cnt_row + 4)].font = font
                            ws["D" + str(cnt_row + 5)] = "Descrição"
                            ws["D" + str(cnt_row + 5)].font = font
                            ws["D" + str(cnt_row + 2)] = "Integrações sobre " + str(
                                plan_build[0].fund.template.name
                            )
                            ws["D" + str(cnt_row + 2)].font = font
                            ws["D" + str(cnt_row + 3)] = plan_build[
                                0
                            ].fund.template.name
                            ws["D" + str(cnt_row + 3)].font = font
                            ws["D" + str(cnt_row + 4)] = str(item.classes)
                            ws["D" + str(cnt_row + 4)].font = font
                            ws["D" + str(cnt_row + 5)] = "Descrição"
                            ws["D" + str(cnt_row + 5)].font = font
                            ws["D" + str(cnt_row + 5)].fill = grayFill
                            ws["E" + str(cnt_row + 5)] = "Data base"
                            ws["E" + str(cnt_row + 5)].font = font
                            ws["E" + str(cnt_row + 5)].fill = grayFill
                            ws["F" + str(cnt_row + 5)] = "Súmula 381"
                            ws["F" + str(cnt_row + 5)].font = font
                            ws["F" + str(cnt_row + 5)].fill = grayFill
                            ws["G" + str(cnt_row + 5)] = "É extraconcursal"
                            ws["G" + str(cnt_row + 5)].font = font
                            ws["G" + str(cnt_row + 5)].fill = grayFill
                            ws["H" + str(cnt_row + 5)] = "Valor histórico"
                            ws["H" + str(cnt_row + 5)].font = font
                            ws["H" + str(cnt_row + 5)].fill = grayFill
                            ws["I" + str(cnt_row + 5)
                               ] = "Indíce na data base"
                            ws["I" + str(cnt_row + 5)].font = font
                            ws["I" + str(cnt_row + 5)].fill = grayFill
                            ws["J" + str(cnt_row + 5)
                               ] = "Indíce na recuperação"
                            ws["J" + str(cnt_row + 5)].font = font
                            ws["J" + str(cnt_row + 5)].fill = grayFill
                            ws["K" + str(cnt_row + 5)] = "Valor corrigido"
                            ws["K" + str(cnt_row + 5)].font = font
                            ws["K" + str(cnt_row + 5)].fill = grayFill
                            cnt_row = cnt_row + 6
                            sum_total = 0
                            sum_total1 = 0
                            for item1 in plan_build:
                                if item1.status == "C":
                                    ws["D" + str(cnt_row)] = str(
                                        item1.description
                                    ).strip()
                                    ws["E" + str(cnt_row)].alignment = Alignment(
                                        horizontal="center"
                                    )
                                    ws["E" + str(cnt_row)] = datetime.strftime(
                                        item1.data_base, "%d/%m/%Y"
                                    )
                                    ws["F" + str(cnt_row)].alignment = Alignment(
                                        horizontal="center"
                                    )
                                    ws["F" + str(cnt_row)] = (
                                        "Sim" if item1.summary == True else "Não"
                                    )
                                    ws["G" + str(cnt_row)].alignment = Alignment(
                                        horizontal="center"
                                    )
                                    ws["G" + str(cnt_row)] = (
                                        "Sim"
                                        if item1.is_extraconcursal == True
                                        else "Não"
                                    )
                                    ws["H" + str(cnt_row)].alignment = Alignment(
                                        horizontal="right"
                                    )
                                    ws["H" + str(cnt_row)] = (
                                        "{:,.2f}".format(
                                            float(item1.historical_value)
                                        )
                                        .strip()
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                        if "historical_value" in item1._dict.keys()
                                        else "{:,.2f}".format(0)
                                        .strip()
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                    )
                                    sum_total += (
                                        float(item1.historical_value)
                                        if "historical_value" in item1._dict.keys()
                                        else 0
                                    )
                                    try:
                                        ws[
                                            "I" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["I" + str(cnt_row)] = (
                                            "{:,.5f}".format(
                                                float(
                                                    item1.monetarycorrectionintegrations.index_data_base
                                                )
                                            )
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                            if item1.monetarycorrectionintegrations
                                            else "{:,.5f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                        ws[
                                            "J" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["J" + str(cnt_row)] = (
                                            "{:,.5f}".format(
                                                float(
                                                    item1.monetarycorrectionintegrations.index_recovering
                                                )
                                            )
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                            if item1.monetarycorrectionintegrations
                                            else "{:,.5f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                        ws[
                                            "K" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["K" + str(cnt_row)] = (
                                            "{:,.2f}".format(
                                                float(
                                                    item1.monetarycorrectionintegrations.corrected_value
                                                )
                                            )
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                            if item1.monetarycorrectionintegrations
                                            else "{:,.5f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                        sum_total1 += (
                                            float(
                                                item1.monetarycorrectionintegrations.corrected_value
                                            )
                                            if item1.monetarycorrectionintegrations
                                            else 0
                                        )
                                    except:
                                        ws[
                                            "I" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["I" + str(cnt_row)] = (
                                            "{:,.5f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                        ws[
                                            "J" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["J" + str(cnt_row)] = (
                                            "{:,.5f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                        ws[
                                            "K" + str(cnt_row)
                                            ].alignment = Alignment(horizontal="right")
                                        ws["K" + str(cnt_row)] = (
                                            "{:,.2f}".format(0)
                                            .strip()
                                            .replace(".", "-")
                                            .replace(",", ".")
                                            .replace("-", ",")
                                        )
                                    cnt_row = cnt_row + 1
                            ws["D" + str(cnt_row)] = "Total"
                            ws["D" + str(cnt_row)].font = font
                            ws["H" + str(cnt_row)] = "{:,.2f}".format(
                                sum_total
                            ).strip()
                            ws["H" + str(cnt_row)].font = font
                            ws["H" + str(cnt_row)].alignment = Alignment(
                                horizontal="right"
                            )
                            ws["K" + str(cnt_row)] = "{:,.2f}".format(
                                sum_total1
                            ).strip()
                            ws["K" + str(cnt_row)].font = font
                            ws["K" + str(cnt_row)].alignment = Alignment(
                                horizontal="right"
                            )
                            cnt_row = cnt_row + 1
                        else:
                            ws["D" + str(cnt_row)] = "Crédito " + \
                                                     item.template.name
                            ws["D" + str(cnt_row)].font = font
                            ws["D" + str(cnt_row + 2)] = "Integrações sobre " + str(
                                item.template.name
                            )
                            ws["D" + str(cnt_row + 2)].font = font
                            ws["D" + str(cnt_row + 3)] = item.name
                            ws["D" + str(cnt_row + 3)].font = font
                            ws["D" + str(cnt_row + 4)] = str(item.classes)
                            ws["D" + str(cnt_row + 4)].font = font
                            ws["D" + str(cnt_row + 5)] = "Descrição"
                            ws["D" + str(cnt_row + 5)].font = font
                            ws["D" + str(cnt_row + 5)].fill = grayFill
                            ws["E" + str(cnt_row + 5)] = "Data base"
                            ws["E" + str(cnt_row + 5)].font = font
                            ws["E" + str(cnt_row + 5)].fill = grayFill
                            ws["F" + str(cnt_row + 5)] = "Súmula 381"
                            ws["F" + str(cnt_row + 5)].font = font
                            ws["F" + str(cnt_row + 5)].fill = grayFill
                            ws["G" + str(cnt_row + 5)] = "É extraconcursal"
                            ws["G" + str(cnt_row + 5)].font = font
                            ws["G" + str(cnt_row + 5)].fill = grayFill
                            ws["H" + str(cnt_row + 5)] = "Valor histórico"
                            ws["H" + str(cnt_row + 5)].font = font
                            ws["H" + str(cnt_row + 5)].fill = grayFill
                            ws["I" + str(cnt_row + 5)
                               ] = "Indíce na data base"
                            ws["I" + str(cnt_row + 5)].font = font
                            ws["I" + str(cnt_row + 5)].fill = grayFill
                            ws["J" + str(cnt_row + 5)
                               ] = "Indíce na recuperação"
                            ws["J" + str(cnt_row + 5)].font = font
                            ws["J" + str(cnt_row + 5)].fill = grayFill
                            ws["K" + str(cnt_row + 5)] = "Valor corrigido"
                            ws["K" + str(cnt_row + 5)].font = font
                            ws["K" + str(cnt_row + 5)].fill = grayFill
                            cnt_row = cnt_row + 6
                        cnt_row = cnt_row + 2
                        plan_build1 = item.get_all_statement_funds()
                        if plan_build1 and len(plan_build1) > 0:
                            ws["D" + str(cnt_row)
                               ] = str(item.template.name)
                            ws["D" + str(cnt_row)].font = font
                            ws["D" + str(cnt_row + 1)] = "Data base"
                            ws["D" + str(cnt_row + 1)].font = font
                            ws["D" + str(cnt_row + 1)].fill = grayFill
                            ws["E" + str(cnt_row + 1)] = "Súmula 381"
                            ws["E" + str(cnt_row + 1)].font = font
                            ws["E" + str(cnt_row + 1)].fill = grayFill
                            ws["F" + str(cnt_row + 1)] = "É extraconcursal"
                            ws["F" + str(cnt_row + 1)].font = font
                            ws["F" + str(cnt_row + 1)].fill = grayFill
                            ws["G" + str(cnt_row + 1)] = "Valor histórico"
                            ws["G" + str(cnt_row + 1)].font = font
                            ws["G" + str(cnt_row + 1)].fill = grayFill
                            ws["H" + str(cnt_row + 1)
                               ] = "Indíce na data base"
                            ws["H" + str(cnt_row + 1)].font = font
                            ws["H" + str(cnt_row + 1)].fill = grayFill
                            ws["I" + str(cnt_row + 1)
                               ] = "Indíce na recuperação"
                            ws["I" + str(cnt_row + 1)].font = font
                            ws["I" + str(cnt_row + 1)].fill = grayFill
                            ws["J" + str(cnt_row + 1)] = "Valor corrigido"
                            ws["J" + str(cnt_row + 1)].font = font
                            ws["J" + str(cnt_row + 1)].fill = grayFill
                            cnt_row = cnt_row + 2
                            sum_total = 0
                            sum_total1 = 0
                            for item2 in plan_build1:
                                if item2.status == "C":
                                    ws["D" + str(cnt_row)] = datetime.strftime(
                                        item2.data_base, "%d/%m/%Y"
                                    )
                                    ws["E" + str(cnt_row)].alignment = Alignment(
                                        horizontal="center"
                                    )
                                    ws["E" + str(cnt_row)] = (
                                        "Sim" if item2.summary == True else "Não"
                                    )
                                    ws["F" + str(cnt_row)].alignment = Alignment(
                                        horizontal="center"
                                    )
                                    ws["F" + str(cnt_row)] = (
                                        "Sim"
                                        if item2.is_extraconcursal == True
                                        else "Não"
                                    )
                                    ws["G" + str(cnt_row)].alignment = Alignment(
                                        horizontal="right"
                                    )
                                    ws["G" + str(cnt_row)] = (
                                        "{:,.2f}".format(
                                            float(item2.historical_value)
                                        )
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                    )
                                    value_index = item2.get_monetary_correction()
                                    ws["H" + str(cnt_row)].alignment = Alignment(
                                        horizontal="right"
                                    )
                                    ws["H" + str(cnt_row)] = (
                                        "{:,.5f}".format(
                                            float(
                                                value_index.index_data_base)
                                        )
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                        if value_index
                                           and "index_data_base"
                                           in value_index._dict.keys()
                                        else ""
                                    )
                                    ws["I" + str(cnt_row)].alignment = Alignment(
                                        horizontal="right"
                                    )
                                    ws["I" + str(cnt_row)] = (
                                        "{:,.5f}".format(
                                            float(
                                                value_index.index_recovering)
                                        )
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                        if value_index
                                           and "index_recovering"
                                           in value_index._dict.keys()
                                        else ""
                                    )
                                    ws["J" + str(cnt_row)].alignment = Alignment(
                                        horizontal="right"
                                    )
                                    ws["J" + str(cnt_row)] = (
                                        "{:,.2f}".format(
                                            float(
                                                str(value_index).split(" - ")[2])
                                        )
                                        .replace(".", "-")
                                        .replace(",", ".")
                                        .replace("-", ",")
                                        if value_index
                                        else ""
                                    )
                                    sum_total += (
                                        float(
                                            float(str(item2.historical_value)))
                                        if item2.historical_value
                                        else 0
                                    )
                                    sum_total1 += (
                                        float(
                                            float(
                                                str(value_index).split(" - ")[2])
                                        )
                                        if value_index
                                        else 0
                                    )
                                    cnt_row = cnt_row + 1
                            ws["D" + str(cnt_row)] = "Total"
                            ws["D" + str(cnt_row)].font = font
                            ws["G" + str(cnt_row)] = "{:,.2f}".format(
                                sum_total
                            ).strip()
                            ws["G" + str(cnt_row)].font = font
                            ws["G" + str(cnt_row)].alignment = Alignment(
                                horizontal="right"
                            )
                            ws["J" + str(cnt_row)] = "{:,.2f}".format(
                                sum_total1
                            ).strip()
                            ws["J" + str(cnt_row)].font = font
                            ws["J" + str(cnt_row)].alignment = Alignment(
                                horizontal="right"
                            )
                            cnt_row = cnt_row + 1
                        else:
                            ws["D" + str(cnt_row)
                               ] = str(item.template.name)
                            ws["D" + str(cnt_row)].font = font
                            ws["D" + str(cnt_row + 1)] = "Data base"
                            ws["D" + str(cnt_row + 1)].font = font
                            ws["D" + str(cnt_row + 1)].fill = grayFill
                            ws["E" + str(cnt_row + 1)] = "Súmula 381"
                            ws["E" + str(cnt_row + 1)].font = font
                            ws["E" + str(cnt_row + 1)].fill = grayFill
                            ws["F" + str(cnt_row + 1)] = "É extraconcursal"
                            ws["F" + str(cnt_row + 1)].font = font
                            ws["F" + str(cnt_row + 1)].fill = grayFill
                            ws["G" + str(cnt_row + 1)] = "Valor histórico"
                            ws["G" + str(cnt_row + 1)].font = font
                            ws["G" + str(cnt_row + 1)].fill = grayFill
                            ws["H" + str(cnt_row + 1)
                               ] = "Indíce na data base"
                            ws["H" + str(cnt_row + 1)].font = font
                            ws["H" + str(cnt_row + 1)].fill = grayFill
                            ws["I" + str(cnt_row + 1)
                               ] = "Indíce na recuperação"
                            ws["I" + str(cnt_row + 1)].font = font
                            ws["I" + str(cnt_row + 1)].fill = grayFill
                            ws["J" + str(cnt_row + 1)] = "Valor corrigido"
                            ws["J" + str(cnt_row + 1)].font = font
                            ws["J" + str(cnt_row + 1)].fill = grayFill
                            cnt_row = cnt_row + 3
        for sheet in archive_view:
            if sheet.sheet_state == "hidden":
                continue
            if type(sheet.title) == str and sheet.title.find("JUCA=") >= 0:
                archive_view.remove_sheet(archive_view[sheet.title])
            sheet.title = sheet.title.replace(" Copy", "")
        for sheet in archive_view:
            if sheet.sheet_state == "hidden":
                continue
            for row in reversed(list(sheet.iter_rows())):
                for col in row:
                    if col.value:
                        if col.value.find("JUCALST=") >= 0:
                            col_value = str(col.value)[8:]
                            cnt_ini_row = col.row
                            let_ini_col = col.column_letter

                            if col_value == "NoticeAJ":
                                col.value = ""
                                for item in notice:
                                    set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
                                    set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
                                    set_sheet_number(sheet, cnt_ini_row + 2, let_ini_col, item.coins.value)
                                    let_ini_col = chr(ord(let_ini_col) + 1)

                            elif col_value == "Claim_Creditor":
                                col.value = ""
                                for item in claim_creditor:
                                    set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
                                    set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
                                    set_sheet_number(sheet, cnt_ini_row + 2, let_ini_col, item.coins.value)
                                    let_ini_col = chr(ord(let_ini_col) + 1)

                            elif col_value == "Claim_Lawyer":
                                col.value = ""
                                if claim_lawyer:
                                    set_sheet_value(sheet, cnt_ini_row, let_ini_col, claim_lawyer.classes)
                                    set_sheet_number(sheet, cnt_ini_row + 1, let_ini_col, claim_lawyer.coins.value)

                            elif col_value == "Sheets":  # OK
                                col.value = ""

                                if funds.count() == 0:
                                    delete_rows(sheet, cnt_ini_row - 1, 1)
                                for item in funds:
                                    set_sheet_value(sheet, cnt_ini_row, ['A', 'B'], item.name, force=True)
                                    set_sheet_number(sheet, cnt_ini_row, 'C', item.get_total_summed())
                                    cnt_ini_row += 1

                                statement_pf = calculation.statement.get_statement_pf()
                                if statement_pf:
                                    set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                                                    calculation.statement.statementpf.get_description_display(),
                                                    force=True)
                                    set_sheet_number(sheet, cnt_ini_row, 'C', statement_pf.total)

                                    cnt_ini_row = cnt_ini_row + 1

                                    juca_excel[
                                        'legend_monetary_correction_update'] = statement_pf.legend_monetary_correction_update
                                    juca_excel['index_name'] = calculation.rate.index

                                    tax_days = statement_pf.get_tax_days()

                                    if tax_days:
                                        set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                                                        tax_days.get_description_display(), force=True)
                                        set_sheet_number(sheet, cnt_ini_row, 'C', 5)
                                        cnt_ini_row = cnt_ini_row + 1

                                    default_interest = statement_pf.get_default_interest()
                                    if default_interest:
                                        set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                                                        statement_pf.default_interest_legend, force=True)
                                        set_sheet_number(sheet, cnt_ini_row, 'C', default_interest.value)
                                        cnt_ini_row = cnt_ini_row + 1

                                    default_interest_or_due = statement_pf.get_default_interest_due()
                                    if default_interest_or_due:
                                        set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                                                        default_interest_or_due.get_description_display(), force=True)
                                        set_sheet_number(sheet, cnt_ini_row, 'C', default_interest_or_due.value)

                            elif col_value == "FundDocument":
                                sum_total = 0
                                sum_total1 = 0
                                sum_total2 = 0
                                sum_total3 = 0
                                sum_total4 = 0
                                col.value = ""
                                if fund_document.count() == 0:
                                    delete_rows(sheet, cnt_ini_row - 2, 5)

                                for item in fund_document:
                                    statement_document = (
                                        StatementDocument.objects.filter(
                                            fund_id=item.id
                                        )
                                    )
                                    for item1 in statement_document:
                                        set_sheet_value(sheet, cnt_ini_row, 'A', item, force=True)
                                        set_sheet_value(sheet, cnt_ini_row, 'B', item1.number, alignment='center')
                                        set_sheet_value(sheet, cnt_ini_row, 'C', item1.data_base, alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'D', item1.historical_value,
                                                         alignment='right')
                                        set_sheet_number(sheet, cnt_ini_row, 'E',
                                                         item1.monetarycorrectiondocument.index_data_base,
                                                         alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'F',
                                                         item1.monetarycorrectiondocument.index_recovering,
                                                         alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'G',
                                                         item1.monetarycorrectiondocument.corrected_value,
                                                         alignment='right')
                                        set_sheet_value(sheet, cnt_ini_row, 'H', item1.days, alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'I', item1.default_interest,
                                                         alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'J', item1.fine, alignment='center')
                                        set_sheet_number(sheet, cnt_ini_row, 'K', item1.total_due, alignment='center')
                                        cnt_ini_row = cnt_ini_row + 1
                                        sum_total += float(item1.historical_value)
                                        sum_total1 += float(
                                            item1.monetarycorrectiondocument.corrected_value
                                        )
                                        sum_total2 += float(
                                            item1.default_interest)
                                        sum_total3 += float(item1.fine)
                                        sum_total4 += float(
                                            item1.monetarycorrectiondocument.corrected_value
                                            + item1.fine
                                            + item1.default_interest
                                        )
                                if len(fund_document) > 0:
                                    sheet["A" + str(cnt_ini_row)] = "Total"
                                    sheet["A" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "D" + str(cnt_ini_row)
                                        ] = "{:,.2f}".format(sum_total).strip()
                                    sheet["D" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "D" + str(cnt_ini_row)
                                        ].alignment = Alignment(horizontal="right")
                                    sheet[
                                        "G" + str(cnt_ini_row)
                                        ] = "{:,.2f}".format(sum_total1).strip()
                                    sheet["G" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "G" + str(cnt_ini_row)
                                        ].alignment = Alignment(horizontal="right")
                                    sheet[
                                        "I" + str(cnt_ini_row)
                                        ] = "{:,.2f}".format(sum_total2).strip()
                                    sheet["I" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "I" + str(cnt_ini_row)
                                        ].alignment = Alignment(horizontal="right")
                                    sheet[
                                        "J" + str(cnt_ini_row)
                                        ] = "{:,.2f}".format(sum_total3).strip()
                                    sheet["J" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "J" + str(cnt_ini_row)
                                        ].alignment = Alignment(horizontal="right")
                                    sheet[
                                        "K" + str(cnt_ini_row)
                                        ] = "{:,.2f}".format(sum_total4).strip()
                                    sheet["K" +
                                          str(cnt_ini_row)].font = font
                                    sheet[
                                        "K" + str(cnt_ini_row)
                                        ].alignment = Alignment(horizontal="right")
                                    cnt_ini_row = cnt_ini_row + 2

                            elif col_value == "Premises":
                                col.value = ""
                                for item in premises:
                                    set_sheet_value(sheet, cnt_ini_row, ['A', 'G'], item, force=True)
                                    cnt_ini_row = cnt_ini_row + 1

                            elif col_value == "NoticeAJ_Vert":
                                col.value = "Edital AJ:"
                                force = False
                                for item in notice:
                                    set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                                                    force=force)
                                    set_sheet_value(sheet, cnt_ini_row, 'C', item.coins, alignment='center')
                                    set_sheet_number(sheet, cnt_ini_row, 'D', item.coins.value, alignment='center')
                                    set_sheet_value(sheet, cnt_ini_row, 'E', recovering_name)
                                    cnt_ini_row = cnt_ini_row + 1
                                    force = True

                            elif col_value == "Claim_Creditor_Vert":
                                col.value = "Solicitado pelo credor:"
                                force = False
                                for item in claim_creditor:
                                    set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                                                    force=force)
                                    set_sheet_value(sheet, cnt_ini_row, 'C', item.coins, alignment='center')
                                    set_sheet_number(sheet, cnt_ini_row, 'D', item.coins.value, alignment='center')
                                    set_sheet_value(sheet, cnt_ini_row, 'E', recovering_name)
                                    cnt_ini_row = cnt_ini_row + 1
                                    force = True

                            elif col_value == "Claim_Lawyer_Vert":
                                col.value = "Honorários advocatícios:"
                                if claim_lawyer:
                                    set_sheet_value(sheet, cnt_ini_row, 'B', claim_lawyer.classes, alignment='left')
                                    set_sheet_value(sheet, cnt_ini_row, 'C', claim_lawyer.coins, alignment='center')
                                    set_sheet_number(sheet, cnt_ini_row, 'D', claim_lawyer.coins.value,
                                                     alignment='center')
                                    set_sheet_value(sheet, cnt_ini_row, 'E', recovering_name)

                        if col.value.find("JUCAD=") >= 0:
                            value = replace_key('JUCAD=',col.value, juca_excel)
                            print(value, 'va JUCAd\n')
                            col.value = ''
                            if str(value) == 'None':
                                delete_rows(sheet, col.row)
                            else:
                                col.value = value

                        if col.value.find("JUCA=") >= 0:
                            value = replace_key('JUCA=',col.value, juca_excel)

                            if str(value) == 'None':
                                value = ''
                            col.value = value

        archive_view.save(new_name_view)

        list_html = {}
        list_pdf = []
        for sheet in archive_view:
            if sheet.sheet_state == "hidden":
                continue
            out_stream = xlsx2html(
                new_name_view, sheet=sheet.title, parse_formula=False
            )
            out_stream.seek(0)
            result_html = out_stream.read()
            result_html = (
                result_html.replace("\n    ", "")
                .replace("\n", "")
                .replace('\\"', '"')
            )
            list_html[sheet._WorkbookChild__title] = result_html
            list_pdf.append(result_html)

        # adjust layout from download
        # for sheet in archive_view:
        #    if sheet['A1'].value == None:
        #        sheet.delete_cols(0)
        #    if sheet['A1'].value == None and sheet['B1'].value and sheet['C1'].value:
        #        sheet.delete_cols(1,3)
        # archive_view.save(new_name_view)

        # Create a HTML File
        with open(new_name_view, "rb") as archive_excel:
            excel_file = archive_excel.read()
            base64_encoded_data = base64.b64encode(excel_file)
            base64_message = base64_encoded_data.decode("latin-1")

        # create a pdf file
        pdfkit.from_string('\n'.join(list_pdf), new_name_pdf, configuration=config)

        with open(new_name_pdf, "rb") as archive_pdf:
            pdf_file = archive_pdf.read()
            base64_encoded_data = base64.b64encode(pdf_file)
            base64_message_pdf = base64_encoded_data.decode("latin-1")

        remove(new_name_view)
        remove(new_name_pdf)

        if export_type == "html":
            return JsonResponse({"html": f'"{str(list_html)}"'})
        if export_type == "xlsx":
            return JsonResponse(data={"excel": f"{base64_message}"})
        if export_type == "pdf":
            return JsonResponse({"pdf": f"{base64_message_pdf}"})
        else:
            return JsonResponse(
                {"html": f'"{str(list_html)}"', "excel": f"{base64_message}", "pdf": f"{base64_message_pdf}"})

    # except BaseException as e:
    #     return JsonResponse({"errors": str(e)})


def replace_key(prefix, text, dicionario):
    text = re.sub(f'{prefix}([^\s]+)', lambda match: f"{dicionario.get(match.group(1), '')}".strip(), text)

    return text
