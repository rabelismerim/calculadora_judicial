import logging
import re
from copy import copy

from openpyxl.utils import get_column_letter

from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from calculation.funds.document.models import StatementDocument, FundDocument
from calculation.models import Calculation
from rates.models import TemplateSlugChoices, FieldTypeChoices
from rates.schemas import TemplateSchema

from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
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

bold_font = Font(bold=True)
bold_white_font = Font(bold=True, color="FFFFFF")  # "FFFFFF" representa a cor branca em hexadecimal

total_merged = 2


def get_nested_attr(obj, attr_str):
    attrs = attr_str.split('.')
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj


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


def set_sheet_value(sheet_, line, column: str or list, value, force=False, alignment=None, font=None, fill=None):
    if force:
        merged_cells_range = sheet_.merged_cells.ranges
        for merged_cell in merged_cells_range:
            if merged_cell.min_row >= line:
                merged_cell.shift(0, 1)
        sheet_.insert_rows(line, 1)

    if isinstance(column, list):
        sheet_.merge_cells(f'{column[0]}{line}:{column[1]}{line}')
        column = column[0]

    column_line = f'{column}{line}'
    sheet_line = sheet_[column_line]
    sheet_line.value = str(value)
    if alignment:
        sheet_line.alignment = Alignment(horizontal=alignment)
    elif column.startswith("C"):
        sheet_line.alignment = Alignment(horizontal='right')

    if font:
        sheet_line.font = font
    if fill:
        sheet_line.fill = fill
    return sheet_


def set_sheet_number(sheet_, line, column, value, force=False, alignment=None, font=None, fill=None):
    try:
        value = "{:,.2f}" \
            .format(value) \
            .replace(".", "|") \
            .replace(",", ".") \
            .replace("|", ",")
    except ValueError:
        pass
    return set_sheet_value(sheet_, line, column, value, force=force, alignment=alignment, font=font, fill=fill)


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
        return SheetExcel(**kwargs).generate()


def replace_key(prefix, text, dicionario):
    return re.sub(f'{prefix}([^\s]+)', lambda match: f"{dicionario.get(match.group(1), '')}".strip(), text)


class SheetExcel:
    def new_archive(self, filename):
        sequence = 0
        new_name = filename.split("/")[-1]
        path = "/".join(filename.split("/")[:-1])
        name_file = new_name
        while True:
            new_name = f"{str(sequence)}_{name_file}"
            if exists(f"{path}/{new_name}"):
                sequence += 1
            else:
                break
        return f"{path}/{new_name}"

    def __init__(self, **kwargs):
        # Objects to publish in sheet
        self.name_report = kwargs.get("export_type").split(';')[0] if len(
            kwargs.get("export_type").split(';')) > 1 else kwargs.get("export_type")
        self.export_type = kwargs.get("export_type").split(';')[1] if len(
            kwargs.get("export_type").split(';')) > 1 else None

        self.sheet_template = SheetsTemplate.objects.filter(name=self.name_report).first()
        calculation_id = kwargs.get('calculation_id')
        self.calculation = Calculation.objects.filter(id=calculation_id).first()
        self.creditor = self.calculation.creditor
        self.statement = self.calculation.get_statement()

        self.funds = self.calculation.funds_set.all()
        self.premises = self.calculation.get_premises()
        self.fund_document = FundDocument.objects.filter(
            calculation_id=calculation_id)

        self.notice = self.creditor.get_notice()
        self.claim_creditor = self.creditor.get_claims_creditor().order_by("classes__classe")

        self.claim_lawyer = self.creditor.get_claim_lawyer()

        self.recovering = self.creditor.recovering

        self.recovering_name = self.recovering.entity.name
        self.project = self.creditor.recovering.project
        self.entity = self.creditor.entity

        self.court = self.project.court

        self.sheet_template_name = self.sheet_template.file.name.upper()
        # open the archive and process
        self.archive_view = xl.load_workbook(
            "uploads/"
            + self.sheet_template_name,
            read_only=False,
        )
        self.new_name_view = self.new_archive(
            "uploads/"
            + self.sheet_template_name.replace(".XLSX", "-VIEW.XLSX")
        )
        self.new_name_pdf = self.new_archive(
            "uploads/"
            + self.sheet_template_name.replace(".XLSX", ".PDF")
        )

        self.juca_excel = {
            'credor_name': self.entity.name,
            'legal_number': self.entity.legal_number,
            'incident_number': self.calculation.incident_number,
            'court_name': self.court.description,
            'has_edital': 'Sim' if self.calculation.has_edital else 'Não',
            'has_advocative_hours': 'Sim' if self.calculation.has_advocative_hours else 'Não',
            'recovering_name': self.recovering_name,
            'admission': self.creditor.admission,
            'dismissal': self.creditor.dismissal,
            'date_rj_request': self.calculation.get_date_rj_request(),
            'date_rj_filing,': self.calculation.get_date_rj_filing(),
            'date_citation,': self.calculation.get_date_citation(),
            'legend_default_interest': self.calculation.get_legend_default_interest(),
            'legend_fine': self.calculation.get_legend_fine(),
            'fine': self.calculation.get_fine(),
            'default_interest': self.calculation.get_default_interest(),
            'legend_advocative_hours': self.calculation.get_legend_advocative_hours(),
            'advocative_hours': self.calculation.get_advocative_hours(),
            'executor': self.calculation.executor,
            'reviewer': self.calculation.reviewer,
            'approver': self.calculation.approver,
            'legend_impugnacao_or_habilitacao': self.statement.get_conclusion_display(),
            'legend_citation_filling': 'Data da citação:' if self.calculation.is_citation() else 'Data do ajuizamento da RJ:',
        }

    def set_formula_notice_aj(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = ""
        for item in self.notice:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
            set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
            set_sheet_number(sheet, cnt_ini_row + 2, let_ini_col, item.coins.value)
            let_ini_col = chr(ord(let_ini_col) + 1)

    def set_formula_claim_creditor(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = ""
        for item in self.claim_creditor:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
            set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
            set_sheet_number(sheet, cnt_ini_row + 2, let_ini_col, item.coins.value)
            let_ini_col = chr(ord(let_ini_col) + 1)

    def set_formula_claim_lawyer(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = ""
        if self.claim_lawyer:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col, self.claim_lawyer.classes)
            set_sheet_number(sheet, cnt_ini_row + 1, let_ini_col, self.claim_lawyer.coins.value)

    def set_formula_sheets(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = ""

        if not self.funds.exists():
            print('deletando\n')
            delete_rows(sheet, cnt_ini_row - 1, 1)
        for item in self.funds:
            set_sheet_value(sheet, cnt_ini_row, ['A', 'B'], item.name, force=True)
            set_sheet_number(sheet, cnt_ini_row, 'C', item.get_total_summed())
            cnt_ini_row += 1

        statement_pf = self.calculation.statement.get_statement_pf()
        if statement_pf:
            set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                            self.calculation.statement.statementpf.get_description_display(),
                            force=True)
            set_sheet_number(sheet, cnt_ini_row, 'C', statement_pf.total)

            cnt_ini_row = cnt_ini_row + 1

            self.juca_excel[
                'legend_monetary_correction_update'] = statement_pf.legend_monetary_correction_update
            self.juca_excel['index_name'] = self.calculation.rate.index

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

    def set_formula_premises(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = ""
        for item in self.premises:
            set_sheet_value(sheet, cnt_ini_row, ['A', 'G'], item, force=True)
            cnt_ini_row = cnt_ini_row + 1

    def set_formula_notice_aj_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = "Edital AJ:"
        force = False
        for item in self.notice:
            set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                            force=force)
            set_sheet_value(sheet, cnt_ini_row, 'C', item.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D', item.coins.value, alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)
            cnt_ini_row = cnt_ini_row + 1
            force = True

    def set_formula_claim_creditor_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = "Solicitado pelo credor:"
        force = False
        for item in self.claim_creditor:
            set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                            force=force)
            set_sheet_value(sheet, cnt_ini_row, 'C', item.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D', item.coins.value, alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)
            cnt_ini_row = cnt_ini_row + 1
            force = True

    def set_formula_claim_lawyer_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        col.value = "Honorários advocatícios:"
        if self.claim_lawyer:
            set_sheet_value(sheet, cnt_ini_row, 'B', self.claim_lawyer.classes, alignment='left')
            set_sheet_value(sheet, cnt_ini_row, 'C', self.claim_lawyer.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D', self.claim_lawyer.coins.value,
                             alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)

    def set_formula_fund_document(self, sheet, col, cnt_ini_row, let_ini_col):
        sum_total = 0
        sum_total1 = 0
        sum_total2 = 0
        sum_total3 = 0
        sum_total4 = 0
        col.value = ""
        if self.fund_document.count() == 0:
            delete_rows(sheet, cnt_ini_row - 2, 5)

        for item in self.fund_document:
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
        if len(self.fund_document) > 0:
            sheet["A" + str(cnt_ini_row)] = "Total"
            sheet["A" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "D" + str(cnt_ini_row)
                ] = "{:,.2f}".format(sum_total).strip()
            sheet["D" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "D" + str(cnt_ini_row)
                ].alignment = Alignment(horizontal="right")
            sheet[
                "G" + str(cnt_ini_row)
                ] = "{:,.2f}".format(sum_total1).strip()
            sheet["G" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "G" + str(cnt_ini_row)
                ].alignment = Alignment(horizontal="right")
            sheet[
                "I" + str(cnt_ini_row)
                ] = "{:,.2f}".format(sum_total2).strip()
            sheet["I" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "I" + str(cnt_ini_row)
                ].alignment = Alignment(horizontal="right")
            sheet[
                "J" + str(cnt_ini_row)
                ] = "{:,.2f}".format(sum_total3).strip()
            sheet["J" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "J" + str(cnt_ini_row)
                ].alignment = Alignment(horizontal="right")
            sheet[
                "K" + str(cnt_ini_row)
                ] = "{:,.2f}".format(sum_total4).strip()
            sheet["K" +
                  str(cnt_ini_row)].font = bold_font
            sheet[
                "K" + str(cnt_ini_row)
                ].alignment = Alignment(horizontal="right")
            cnt_ini_row = cnt_ini_row + 2

    def set_formula_juca_lst(self, sheet, col):
        col_value = str(col.value)[8:]
        cnt_ini_row = col.row
        let_ini_col = col.column_letter

        value_actions = {
            "NoticeAJ": self.set_formula_notice_aj,
            "Claim_Creditor": self.set_formula_claim_creditor,
            "Claim_Lawyer": self.set_formula_claim_lawyer,
            "Sheets": self.set_formula_sheets,
            "FundDocument": self.set_formula_fund_document,
            "Premises": self.set_formula_premises,
            "NoticeAJ_Vert": self.set_formula_notice_aj_vert,
            "Claim_Creditor_Vert": self.set_formula_claim_creditor_vert,
            "Claim_Lawyer_Vert": self.set_formula_claim_lawyer_vert
        }
        formula = value_actions.get(col_value)
        if formula:
            formula(sheet, col, cnt_ini_row, let_ini_col)

    def generate(self):
        for sheet in self.archive_view:
            if sheet.sheet_state == "hidden":
                continue

            if type(sheet.title) == str and sheet.title.find("JUCA=") >= 0:
                self.set_sheet_juca(sheet)

            sheet.title = sheet.title.replace(" Copy", "")
            for row in reversed(list(sheet.iter_rows())):
                for col in row:
                    if not col.value:
                        continue

                    if col.value.find("JUCALST=") >= 0:
                        self.set_formula_juca_lst(sheet, col)

                    if col.value.find("JUCAD=") >= 0:
                        self.set_formula_jucad(sheet, col)

                    if col.value.find("JUCA=") >= 0:
                        self.set_formula_juca(sheet, col)

        self.archive_view.save(self.new_name_view)

        list_html = {}
        list_pdf = []
        for sheet in self.archive_view:
            if sheet.sheet_state == "hidden":
                continue
            out_stream = xlsx2html(
                self.new_name_view, sheet=sheet.title, parse_formula=False
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

        # Create a HTML File
        with open(self.new_name_view, "rb") as archive_excel:
            excel_file = archive_excel.read()
            base64_encoded_data = base64.b64encode(excel_file)
            base64_message = base64_encoded_data.decode("latin-1")

        # create a pdf file
        pdfkit.from_string('\n'.join(list_pdf), self.new_name_pdf, configuration=config)

        with open(self.new_name_pdf, "rb") as archive_pdf:
            pdf_file = archive_pdf.read()
            base64_encoded_data = base64.b64encode(pdf_file)
            base64_message_pdf = base64_encoded_data.decode("latin-1")

        remove(self.new_name_view)
        remove(self.new_name_pdf)

        if self.export_type == "html":
            return JsonResponse({"html": f'"{str(list_html)}"'})
        if self.export_type == "xlsx":
            return JsonResponse(data={"excel": f"{base64_message}"})
        if self.export_type == "pdf":
            return JsonResponse({"pdf": f"{base64_message_pdf}"})
        else:
            return JsonResponse(
                {"html": f'"{str(list_html)}"', "excel": f"{base64_message}", "pdf": f"{base64_message_pdf}"})

    def set_formula_juca(self, sheet, col):
        value = replace_key('JUCA=', col.value, self.juca_excel)
        if str(value) == 'None':
            value = ''
        col.value = value

    def set_formula_jucad(self, sheet, col):
        value = replace_key('JUCAD=', col.value, self.juca_excel)
        col.value = ''
        if str(value) == 'None':
            delete_rows(sheet, col.row)
        else:
            col.value = value

    def set_sheet_juca(self, sheet):

        if str(sheet.title)[5:] == "Calculation":
            self.set_sheet_calculation(sheet)
        self.archive_view.remove_sheet(self.archive_view[sheet.title])

    def set_sheet_calculation(self, sheet):
        copy_sheet = self.archive_view[sheet.title]
        for item in self.funds:
            cnt_row = 0
            self.archive_view.copy_worksheet(copy_sheet)
            ws = self.archive_view[sheet.title + " Copy"]
            ws.title = item.name
            template = item.template
            template_serializer = TemplateSchema(template).data

            set_sheet_value(ws, cnt_row + 1, ['D', 'K'], 'Memória de cálculo da Administradora Judicial',
                            font=bold_white_font, fill=grayFill)

            # TODO: Pegar a data e a legenda usado para fazer o cálculo
            cnt_row += 2
            set_sheet_value(ws, cnt_row + 1, 'D', 'Correção monetária', font=bold_font)
            set_sheet_value(ws, cnt_row + 1, ['E', 'K'], item.rate.index, font=bold_font)
            cnt_row += 1

            for table in template_serializer['tables']:
                if table['slug'] == TemplateSlugChoices.FUNDS:
                    fund_items = item.get_all_statement_funds()
                    total_funds = getattr(item, 'totalvaluesfunds', None)
                    template_name = template.name
                elif table['slug'] == TemplateSlugChoices.FUNDS_INTEGRATION:
                    total_funds = getattr(item, 'totalvaluesfundsintegrations', None)
                    fund_items = item.get_all_statement_funds_integrations()
                    template_name = f'Integrações sobre {template.name}'
                else:
                    logging.error('Table não mapeada na geração do extrato contábil')
                    continue

                fields = sorted(table['fields'], key=lambda x: x['order'])
                letter = 'D'
                set_sheet_value(ws, cnt_row + 1, letter, template_name, font=bold_font)
                cnt_row += 1
                index_order = {}
                for field in fields:

                    key = field['key']
                    if key == 'status_display':
                        continue

                    set_sheet_value(ws, cnt_row + 1, letter, field['label'], font=bold_font, fill=grayFill)
                    cnt_fund = cnt_row + 2

                    if fund_items:
                        for fund_item in fund_items:

                            value = get_nested_attr(fund_item, key)
                            type_value = field['type']

                            if type_value == FieldTypeChoices.DATE:
                                value = datetime.strftime(value, "%d/%m/%Y")
                            elif type_value == FieldTypeChoices.DATETIME:
                                value = datetime.strftime(value, "%d/%m/%Y %H:%M:%S")
                            elif type_value == FieldTypeChoices.BOOLEAN:
                                value = 'Sim' if value else 'Não'

                            if type_value == FieldTypeChoices.FLOAT:
                                set_sheet_number(ws, cnt_fund, letter, value)
                            else:
                                set_sheet_value(ws, cnt_fund, letter, value)
                            cnt_fund += 1
                    else:
                        set_sheet_value(ws, cnt_fund, letter, '-')
                    index_order[field['order']] = letter
                    letter = chr(ord(letter) + 1)

                count = fund_items.count() or 1
                cnt_row += count + 1

                summary = sorted(table['summary'], key=lambda x: x['order'])
                for summ in summary:
                    key = summ.get('key')
                    order = summ.get('order')

                    if key:
                        if total_funds:
                            value = get_nested_attr(total_funds, key)
                        else:
                            value = '-'
                    else:
                        value = summ['label']

                    if summ['type'] == FieldTypeChoices.FLOAT:
                        set_sheet_number(ws, cnt_row + 1, index_order[order], value, font=bold_font)
                    else:
                        set_sheet_value(ws, cnt_row + 1, index_order[order], value, font=bold_font)

                cnt_row += 2
