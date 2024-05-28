import base64
import logging
import re
from copy import copy
from datetime import datetime
from os import remove
from os.path import exists

import openpyxl as xl
import pdfkit
from calculation.models import Calculation
from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from core.abstract.views import AbstractViewApi
from core.permission.views import CheckHasPermission
from django.http import JsonResponse
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from rates.models import FieldTypeChoices, TemplateSlugChoices
from rates.schemas import TemplateSchema
from rest_framework import permissions
from utils import _, doc
from xlsx2html import xlsx2html

config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

gray_fill = PatternFill(start_color="00C0C0C0",
                        end_color="00C0C0C0", fill_type="solid")
green_fill = PatternFill(start_color='86BC25',
                         end_color='86BC25', fill_type='solid')
bold_font = Font(bold=True)
# "FFFFFF" representa a cor branca em hexadecimal
bold_white_font = Font(bold=True, color="FFFFFF")
# "FFFFFF" representa a cor branca em hexadecimal
underline_font = Font(bold=True, color="FFFFFF", underline="single")

total_merged = 2


def get_nested_attr(obj, attr_str):
    """
    Obtém um atributo aninhado de um objeto.

    Args:
    - obj: Objeto a ser acessado.
    - attr_str (str): String contendo o caminho do atributo aninhado separado por pontos.

    Returns:
    - object: Valor do atributo aninhado.
    """
    attrs = attr_str.split('.')
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj


def get_nesteds_attr(objs, attr_str):
    """
    Obtém um atributo aninhado de uma lista de objetos.

    Args:
    - objs (list): Lista de objetos.
    - attr_str (str): String contendo o caminho do atributo aninhado separado por pontos.

    Returns:
    - object: Valor do atributo aninhado.
    """
    for obj in objs:
        try:
            return get_nested_attr(obj, attr_str)
        except AttributeError as e:
            logging.error(e)


def move_cell(cell, rows: int, cols: int, preserve_original=False) -> None:
    """
    Move uma célula na planilha para uma nova posição especificada por linhas e colunas.

    Args:
    - cell: Célula a ser movida.
    - rows (int): Número de linhas a serem movidas.
    - cols (int): Número de colunas a serem movidas.
    - preserve_original (bool): Indica se o valor original da célula deve ser mantido (padrão é False).
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
    """
    Define o valor de uma célula na planilha.

    Args:
    - sheet_ (Sheet): Planilha onde será definido o valor.
    - line (int): Número da linha da célula.
    - column (str or list): Nome da coluna ou lista de duas colunas para mesclar células.
    - value: Valor a ser definido na célula.
    - force (bool): Indica se a ação deve ser forçada (padrão é False).
    - alignment (str): Alinhamento do texto na célula.
    - font (Font): Fonte a ser aplicada na célula.
    - fill (PatternFill): Preenchimento da célula.

    Returns:
    - Sheet: Planilha com o valor definido na célula.
    """
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
    """
    Define um valor numérico formatado em uma célula na planilha.

    Args:
    - sheet_ (Sheet): Planilha onde será definido o valor.
    - line (int): Número da linha da célula.
    - column (str): Nome da coluna.
    - value: Valor numérico a ser definido na célula.
    - force (bool): Indica se a ação deve ser forçada (padrão é False).
    - alignment (str): Alinhamento do texto na célula.
    - font (Font): Fonte a ser aplicada na célula.
    - fill (PatternFill): Preenchimento da célula.

    Returns:
    - Sheet: Planilha com o valor numérico definido na célula.
    """
    try:
        value = "{:,.2f}" \
            .format(value) \
            .replace(".", "|") \
            .replace(",", ".") \
            .replace("|", ",")
    except (ValueError, TypeError) as e:
        logging.info(e)
    return set_sheet_value(sheet_, line, column, value, force=force, alignment=alignment, font=font, fill=fill)


def delete_rows(sheet_, line, quantity=1):
    """
    Remove linhas na planilha.

    Args:
    - sheet_ (Sheet): Planilha onde as linhas serão removidas.
    - line (int): Número da linha inicial a ser removida.
    - quantity (int): Quantidade de linhas a serem removidas (padrão é 1).

    Returns:
    - None
    """
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
    def get(self, request, *args, **kwargs):
        return SheetExcel(**kwargs).generate()


def replace_key(prefix, text, dicionario):
    return re.sub(f'{prefix}([^\s]+)', lambda match: f"{dicionario.get(match.group(1), '')}".strip(), text)


class SheetExcel:
    """
    Classe que manipula e processa dados em uma planilha do Excel com base em parâmetros fornecidos.

    Atributos:
    - name_report (str): Nome do relatório.
    - export_type (str): Tipo de exportação.
    - sheet_template (SheetsTemplate): Objeto representando o modelo da planilha.
    - calculation (Calculation): Objeto representando o cálculo associado.
    - creditor (Creditor): Objeto representando o credor associado ao cálculo.
    - statement (Statement): Objeto representando a declaração associada ao cálculo.
    - funds (QuerySet): Conjunto de fundos associados ao cálculo.
    - premises (Premises): Premissas associadas ao cálculo.
    - fund_document (QuerySet): Conjunto de documentos de fundos associados ao cálculo.
    - notice (Notice): Objeto representando o aviso associado ao credor.
    - claim_creditor (QuerySet): Conjunto de reivindicações do credor ordenadas por classe.
    - claim_lawyer (ClaimLawyer): Objeto representando as reivindicações do advogado.
    - recovering (Recovering): Objeto representando a recuperação associada ao credor.
    - recovering_name (str): Nome da recuperação.
    - project (Project): Objeto representando o projeto associado à recuperação.
    - entity (Entity): Objeto representando a entidade associada ao credor.
    - court (Court): Objeto representando o tribunal associado ao projeto.

    Métodos:
    - generate(): Gera e processa o arquivo Excel com base nas definições fornecidas.

    Métodos Internos:
    - new_archive(filename): Cria um novo nome de arquivo para evitar duplicatas.
    - set_formula_notice_aj(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas de avisos judiciais.
    - set_formula_claim_creditor(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas de reivindicações do credor.
    - set_formula_claim_lawyer(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas de honorários advocatícios.
    - set_formula_sheets(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas relacionadas a folhas.
    - set_formula_premises(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas de premissas.
    - set_formula_fund_document(sheet, col, cnt_ini_row, let_ini_col): Define fórmulas de documentos de fundos.
    - set_formula_juca_lst(sheet, col): Define fórmulas com base em valores específicos.
    - set_formula_juca(sheet, col): Define fórmulas específicas da variável 'juca_excel' em uma planilha.
    - set_formula_jucad(sheet, col): Define fórmulas específicas da variável 'juca_excel' e, se necessário, deleta a linha.
    - set_sheet_juca(sheet): Configura a planilha com base em condições específicas.
    - set_sheet_calculation(sheet): Configura a planilha de cálculo com base nas definições relacionadas aos fundos.
    - set_template(sheet, item, cnt_row, force=False, has_headers=False): Define um template específico em uma planilha para um item fornecido.
    """

    def new_archive(self, filename):
        """
        Cria um novo nome de arquivo para evitar duplicatas adicionando um número de sequência ao nome do arquivo.

        Args:
        - filename (str): O nome do arquivo para o qual um novo nome será gerado.

        Returns:
        - str: O novo nome de arquivo gerado.
        """
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
        """
        Inicializa a classe SheetExcel com os parâmetros fornecidos.

        Args:
        - **kwargs: Parâmetros chave-valor fornecidos para inicializar a classe.

        """
        self.name_report = kwargs.get("export_type").split(';')[0] if len(
            kwargs.get("export_type").split(';')) > 1 else kwargs.get("export_type")
        self.export_type = kwargs.get("export_type").split(';')[1] if len(
            kwargs.get("export_type").split(';')) > 1 else None

        self.name_report = f'{self.name_report}_V1'
        self.sheet_template = SheetsTemplate.objects.filter(
            name=self.name_report).first()
        calculation_id = kwargs.get('calculation_id')
        self.calculation = Calculation.objects.filter(
            id=calculation_id).first()
        self.creditor = self.calculation.creditor
        self.statement = self.calculation.get_statement()

        self.funds = self.calculation.funds_set.all()
        self.funds_danos = self.calculation.funddanos_set.all()
        self.premises = self.calculation.get_premises()
        self.fund_document = self.calculation.funddocument_set.all()

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
            self.sheet_template.file, read_only=False)
        self.new_name_view = self.new_archive(
            "media/"
            + self.sheet_template_name.replace(".XLSX", "-VIEW.XLSX")
        )
        self.new_name_pdf = self.new_archive(
            "media/"
            + self.sheet_template_name.replace(".XLSX", ".PDF")
        )

        self.juca_excel = {
            'credor_name': self.entity.name,
            'legal_number': self.entity.legal_number,
            'process_number': self.calculation.incident_number,
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
            'legend_impugnacao_or_habilitacao': self.statement.get_conclusion_display() if self.statement else '',
            'legend_citation_filling': 'Data da citação:' if self.calculation.is_citation() else 'Data do ajuizamento da RJ:',
        }

    def set_formula_notice_aj(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a avisos judiciais em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.

        """
        col.value = ""
        for item in self.notice:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
            set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
            set_sheet_number(sheet, cnt_ini_row + 2,
                             let_ini_col, item.coins.value)
            let_ini_col = chr(ord(let_ini_col) + 1)

    def set_formula_claim_creditor(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a reivindicações de credores em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""
        for item in self.claim_creditor:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col, item.classes)
            set_sheet_value(sheet, cnt_ini_row + 1, let_ini_col, item.coins)
            set_sheet_number(sheet, cnt_ini_row + 2,
                             let_ini_col, item.coins.value)
            let_ini_col = chr(ord(let_ini_col) + 1)

    def set_formula_claim_lawyer(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a honorários advocatícios em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""
        if self.claim_lawyer:
            set_sheet_value(sheet, cnt_ini_row, let_ini_col,
                            self.claim_lawyer.classes)
            set_sheet_number(sheet, cnt_ini_row + 1, let_ini_col,
                             self.claim_lawyer.coins.value)

    def set_formula_sheets(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a sheets em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""

        if not self.funds.exists():
            delete_rows(sheet, cnt_ini_row - 1, 1)
        for item in self.funds:
            set_sheet_value(sheet, cnt_ini_row, [
                'A', 'B'], item.name, force=True)
            set_sheet_number(sheet, cnt_ini_row, 'C', item.get_total_summed())
            cnt_ini_row += 1

        statement = getattr(self.calculation, 'statement', None)

        if not statement:
            return

        statement_pf = self.calculation.statement.get_statement_pf()

        if statement_pf:
            # TODO MARCELO: verificar por que não apareceu o deposito recursal

            set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                            self.calculation.statement.statementpf.get_description_display(),
                            force=True)
            set_sheet_number(sheet, cnt_ini_row, 'C', statement_pf.total)

            cnt_ini_row = cnt_ini_row + 1

            self.juca_excel[
                'legend_monetary_correction_update'] = statement_pf.legend_monetary_correction_update
            self.juca_excel['index_name'] = self.calculation.rate.index
            self.juca_excel['legend_default_interest'] = statement_pf.default_interest_legend
            self.juca_excel['default_interest'] = statement_pf.get_default_interest()
            self.juca_excel['legend_fine'] = self.calculation.get_legend_fine()
            self.juca_excel['fine'] = self.calculation.get_fine()
            self.juca_excel['legend_advocative_hours'] = self.calculation.get_legend_advocative_hours()
            self.juca_excel['advocative_hours'] = self.calculation.get_advocative_hours()

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
                set_sheet_number(sheet, cnt_ini_row, 'C',
                                 default_interest.value)
                cnt_ini_row = cnt_ini_row + 1

            for fund in self.funds_danos:
                statement_fund = fund.get_statement()
                if statement_fund:
                    set_sheet_value(sheet, cnt_ini_row, [
                                    'A', 'B'], f'Danos {statement_fund.description}', force=True)
                    set_sheet_number(sheet, cnt_ini_row, 'C',
                                     fund.get_total_summed())
                    cnt_ini_row += 1

                    set_sheet_value(sheet, cnt_ini_row, [
                                    'A', 'B'], f'Total {statement_fund.description}', force=True)
                    set_sheet_number(sheet, cnt_ini_row, 'C',
                                     fund.get_total_due_summed())
                    cnt_ini_row += 1

                    set_sheet_value(sheet, cnt_ini_row, [
                                    'A', 'B'], f'Juros {statement_fund.description}', force=True)
                    set_sheet_number(sheet, cnt_ini_row, 'C',
                                     fund.get_total_default_interest())
                    cnt_ini_row += 1

                    set_sheet_value(sheet, cnt_ini_row, ['A', 'B'], f'Juros Danos {statement_fund.description}',
                                    force=True)
                    set_sheet_number(sheet, cnt_ini_row, 'C',
                                     fund.get_total_default_interest())
                    cnt_ini_row += 1

                    set_sheet_value(sheet, cnt_ini_row, ['A', 'B'], f'Total Danos{statement_fund.description}',
                                    force=True)
                    set_sheet_number(sheet, cnt_ini_row, 'C',
                                     fund.get_total_due_summed())
                    cnt_ini_row += 1
            default_interest_or_due = statement_pf.get_default_interest_due()
            if default_interest_or_due:
                set_sheet_value(sheet, cnt_ini_row, ['A', 'B'],
                                default_interest_or_due.get_description_display(), force=True)
                set_sheet_number(sheet, cnt_ini_row, 'C',
                                 default_interest_or_due.value)

    def set_formula_premises(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a premissas em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""
        for item in self.premises:
            set_sheet_value(sheet, cnt_ini_row, ['A', 'G'], item, force=True)
            cnt_ini_row = cnt_ini_row + 1

    def set_formula_notice_aj_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a avisos judiciais em uma planilha, de forma vertical.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.

        """
        col.value = "Edital AJ:"
        force = False
        for item in self.notice:
            set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                            force=force)
            set_sheet_value(sheet, cnt_ini_row, 'C',
                            item.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D',
                             item.coins.value, alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)
            cnt_ini_row = cnt_ini_row + 1
            force = True

    def set_formula_claim_creditor_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a reivindicações de credores em uma planilha, de forma vertical.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = "Solicitado pelo credor:"
        force = False
        for item in self.claim_creditor:
            set_sheet_value(sheet, cnt_ini_row, 'B', item.classes, alignment='left',
                            force=force)
            set_sheet_value(sheet, cnt_ini_row, 'C',
                            item.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D',
                             item.coins.value, alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)
            cnt_ini_row = cnt_ini_row + 1
            force = True

    def set_formula_claim_lawyer_vert(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a honorários advocatícios em uma planilha, de forma vertical.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = "Honorários advocatícios:"
        if self.claim_lawyer:
            set_sheet_value(sheet, cnt_ini_row, 'B',
                            self.claim_lawyer.classes, alignment='left')
            set_sheet_value(sheet, cnt_ini_row, 'C',
                            self.claim_lawyer.coins, alignment='center')
            set_sheet_number(sheet, cnt_ini_row, 'D', self.claim_lawyer.coins.value,
                             alignment='center')
            set_sheet_value(sheet, cnt_ini_row, 'E', self.recovering_name)

    def set_formula_fund_document(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a documentos de fundos em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""
        if self.fund_document.exists():
            set_sheet_value(sheet, col.row, ['A', 'D'], '', fill=green_fill)
            set_sheet_value(sheet, col.row, ['E', 'G'], 'Correção monetária', font=underline_font, fill=green_fill,
                            alignment='center')
            set_sheet_value(sheet, col.row, ['H', 'J'], 'Encargos moratórios', font=underline_font, fill=green_fill,
                            alignment='center')
            set_sheet_value(sheet, col.row, ['K', 'L'], '', fill=green_fill)
        count = 0
        has_headers = False
        for item in self.fund_document:
            self.set_template(sheet, item, cnt_ini_row + count,
                              force=True, has_headers=has_headers)
            count += 1
            has_headers = True

    def set_additional_sentence(self, sheet, col, cnt_ini_row, let_ini_col):
        """
        Define fórmulas relacionadas a honorários advocatícios em uma planilha, de forma vertical.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.
        - cnt_ini_row: A linha inicial na qual as fórmulas serão aplicadas.
        - let_ini_col: A letra da coluna inicial na qual as fórmulas serão aplicadas.
        """
        col.value = ""
        for fund in self.funds_danos:
            statement_fund = fund.get_statement()
            if statement_fund:
                set_sheet_value(sheet, cnt_ini_row, 'C', f'Danos {statement_fund.description}', force=True,
                                alignment='left')
                set_sheet_value(sheet, cnt_ini_row, [
                                'D', 'E'], statement_fund.data_base)
                cnt_ini_row += 1

    def set_formula_juca_lst(self, sheet, col):
        """
        Define fórmulas com base em valores específicos em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.

        """
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
            "Claim_Lawyer_Vert": self.set_formula_claim_lawyer_vert,
            "AdditionalSentence": self.set_additional_sentence
        }
        formula = value_actions.get(col_value)
        if formula:
            formula(sheet, col, cnt_ini_row, let_ini_col)

    def generate(self):
        """
        Gera e processa o arquivo Excel com base nas definições e lógica definidas nos métodos anteriores.

        Returns:
        - Objeto ExportProcessor: Objeto que processa a exportação do arquivo gerado.
        """
        for sheet in self.archive_view:
            if sheet.sheet_state == "hidden":
                continue

            if isinstance(sheet.title, str) and sheet.title.find("JUCA=") >= 0:
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

        return ExportProcessor(self.archive_view, self.new_name_view, self.new_name_pdf,
                               self.export_type).process_export()

    def set_formula_juca(self, sheet, col):
        """
        Define fórmulas específicas da variável 'juca_excel' em uma planilha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.

        """
        value = replace_key('JUCA=', col.value, self.juca_excel)
        if str(value) == 'None':
            value = ''
        col.value = value

    def set_formula_jucad(self, sheet, col):
        """
        Define fórmulas específicas da variável 'juca_excel' em uma planilha e, se necessário, deleta a linha.

        Args:
        - sheet: A planilha na qual as fórmulas serão aplicadas.
        - col: A coluna na planilha onde as fórmulas serão aplicadas.

        """
        value = replace_key('JUCAD=', col.value, self.juca_excel)
        col.value = ''
        if str(value) == 'None':
            delete_rows(sheet, col.row)
        else:
            col.value = value

    def set_sheet_juca(self, sheet):
        """
        Configura a planilha com base em condições específicas.

        Args:
        - sheet: A planilha que será configurada.

        """
        if str(sheet.title)[5:] == "Calculation":
            self.set_sheet_calculation(sheet)
        self.archive_view.remove_sheet(self.archive_view[sheet.title])

    def set_sheet_calculation(self, sheet):
        """
        Configura a planilha de cálculo com base nas definições relacionadas aos fundos.

        Args:
        - sheet: A planilha que será configurada.

        """
        copy_sheet = self.archive_view[sheet.title]
        for item in self.funds:
            cnt_row = 0
            self.archive_view.copy_worksheet(copy_sheet)
            ws = self.archive_view[sheet.title + " Copy"]
            ws.title = item.name

            set_sheet_value(ws, cnt_row + 1, ['A', 'K'], 'Memória de cálculo da Administradora Judicial',
                            font=bold_white_font, fill=gray_fill)

            # TODO: Pegar a data e a legenda usado para fazer o cálculo
            cnt_row += 2
            set_sheet_value(ws, cnt_row + 1, 'A',
                            'Correção monetária', font=bold_font)

            rate = item.get_rate()
            set_sheet_value(ws, cnt_row + 1,
                            ['E', 'K'], rate.index, font=bold_font)
            cnt_row += 1
            self.set_template(ws, item, cnt_row)

        for item in self.funds_danos:
            cnt_row = 0
            self.archive_view.copy_worksheet(copy_sheet)
            ws = self.archive_view[sheet.title + " Copy"]
            ws.title = item.name

            set_sheet_value(ws, cnt_row + 1, ['A', 'K'], 'Memória de cálculo da Administradora Judicial',
                            font=bold_white_font, fill=gray_fill)

            # TODO: Pegar a data e a legenda usado para fazer o cálculo
            cnt_row += 2
            set_sheet_value(ws, cnt_row + 1, 'A',
                            'Correção monetária', font=bold_font)
            rate = item.get_rate()
            set_sheet_value(ws, cnt_row + 1,
                            ['E', 'K'], rate.index, font=bold_font)
            cnt_row += 1
            self.set_template(ws, item, cnt_row)

    def set_template(self, sheet, item, cnt_row, force=False, has_headers=False):
        """
        Define um template específico em uma planilha para um item fornecido.

        Args:
        - sheet: A planilha na qual o template será aplicado.
        - item: O item para o qual o template será definido.
        - cnt_row: A linha na qual o template será iniciado.
        - force (bool, opcional): Indica se o template será forçado.
        - has_headers (bool, opcional): Indica se a planilha tem cabeçalhos.

        """
        TemplateProcessor(sheet, item, cnt_row, self.statement,
                          force, has_headers).set_template()


class ExportProcessor:
    """
    Classe que processa a exportação de arquivos e gera respostas com base nos dados fornecidos.

    Atributos:
    - list_html (dict): Dicionário contendo HTML resultante da exportação.
    - list_pdf (list): Lista contendo dados de PDF resultantes da exportação.

    Métodos:
    - __init__(archive_view, new_name_view, new_name_pdf, export_type): Inicializa a classe ExportProcessor.
    - process_export(): Processa a exportação dos arquivos e gera uma resposta.
    - _generate_html_and_pdf(): Gera dados HTML e PDF a partir das informações fornecidas.
    - _encode_files(): Codifica os arquivos Excel e PDF para base64.
    - _clean_temporary_files(): Remove os arquivos temporários gerados.
    - _prepare_response(base64_message, base64_message_pdf): Prepara a resposta com os dados codificados.

    Métodos Internos:
    - _generate_html_and_pdf(): Gera dados HTML e PDF a partir das informações fornecidas.
    - _encode_files(): Codifica os arquivos Excel e PDF para base64.
    - _clean_temporary_files(): Remove os arquivos temporários gerados.
    - _prepare_response(): Prepara a resposta com os dados codificados.
    """
    list_html = {}
    list_pdf = []

    def __init__(self, archive_view, new_name_view, new_name_pdf, export_type):
        """
        Inicializa a classe ExportProcessor com os parâmetros fornecidos.

        Args:
        - archive_view: Visualização do arquivo.
        - new_name_view: Novo nome para a visualização.
        - new_name_pdf: Novo nome para o arquivo PDF.
        - export_type: Tipo de exportação.
        """
        self.archive_view = archive_view
        self.new_name_view = new_name_view
        self.new_name_pdf = new_name_pdf
        self.export_type = export_type

    def process_export(self):
        """
        Processa a exportação dos arquivos e gera uma resposta.

        Returns:
        - JsonResponse: Resposta JSON com os dados da exportação.
        """
        # try:
        self._generate_html_and_pdf()
        base64_message, base64_message_pdf = self._encode_files()
        response = self._prepare_response(base64_message, base64_message_pdf)
        self._clean_temporary_files()
        return response

        # except Exception as e:
        #     error_message = f"An error occurred: {str(e)}"
        #     return JsonResponse({"error": error_message}, status=500)

    def _generate_html_and_pdf(self):
        """
        Gera dados HTML e PDF a partir das informações fornecidas.
        """
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
            self.list_html[sheet._WorkbookChild__title] = result_html
            self.list_pdf.append(result_html)

    def _encode_files(self):
        """
        Codifica os arquivos Excel e PDF para base64.

        Returns:
        - Tuple[str, str]: Tupla contendo mensagens base64 para Excel e PDF.
        """

        # Create a HTML File
        with open(self.new_name_view, "rb") as archive_excel:
            excel_file = archive_excel.read()
            base64_encoded_data = base64.b64encode(excel_file)
            base64_message = base64_encoded_data.decode("latin-1")

        # Create a pdf file
        pdfkit.from_string('\n'.join(self.list_pdf),
                           self.new_name_pdf, configuration=config)
        # pdfkit.from_string('\n'.join(self.list_pdf), self.new_name_pdf)

        with open(self.new_name_pdf, "rb") as archive_pdf:
            pdf_file = archive_pdf.read()
            base64_encoded_data = base64.b64encode(pdf_file)
            base64_message_pdf = base64_encoded_data.decode("latin-1")

        return base64_message, base64_message_pdf

    def _clean_temporary_files(self):
        """
        Remove os arquivos temporários gerados.
        """
        remove(self.new_name_view)
        remove(self.new_name_pdf)

    def _prepare_response(self, base64_message, base64_message_pdf):
        """
        Prepara a resposta com os dados codificados.

        Args:
        - base64_message: Mensagem base64 para o arquivo Excel.
        - base64_message_pdf: Mensagem base64 para o arquivo PDF.

        Returns:
        - JsonResponse: Resposta JSON com os dados da exportação.
        """
        response_data = {}

        if self.export_type == "html":
            response_data["html"] = f'"{str(self.list_html)}"'
        elif self.export_type == "xlsx":
            response_data["excel"] = f"{base64_message}"
        elif self.export_type == "pdf":
            response_data["pdf"] = f"{base64_message_pdf}"
        else:
            response_data = {
                "html": f'"{str(self.list_html)}"',
                "excel": f"{base64_message}",
                "pdf": f"{base64_message_pdf}"
            }

        return JsonResponse(response_data)


class TemplateProcessor:
    """
    Classe responsável por processar um template de planilha.

    Atributos:
    - index_order (dict): Dicionário contendo a ordem dos índices.
    - sheet: Planilha na qual os dados serão processados.
    - item: Item associado ao template.
    - cnt_row: Contador de linhas na planilha.
    - force (bool): Indica se a ação deve ser forçada.
    - has_headers (bool): Indica se há cabeçalhos na planilha.
    - statement: Declaração associada ao template.

    Métodos:
    - __init__(sheet, item, cnt_row, statement, force=False, has_headers=False): Inicializa a classe TemplateProcessor.
    - set_template(): Define o template na planilha.
    - _process_table(template, table): Processa uma tabela específica do template.
    - _process_fields(table, fund_items, nested_attrs, color, fonte, unique_headers): Processa os campos da tabela.
    - _get_formatted_value(type_value, value): Formata o valor com base no tipo de campo.
    - _process_summary(summary, total_funds): Processa o resumo da tabela.

    Métodos Internos:
    - _process_table(template, table): Processa uma tabela específica do template.
    - _process_fields(table, fund_items, nested_attrs, color, fonte, unique_headers): Processa os campos da tabela.
    - _get_formatted_value(type_value, value): Formata o valor com base no tipo de campo.
    - _process_summary(summary, total_funds): Processa o resumo da tabela.
    """

    def __init__(self, sheet, item, cnt_row, statement, force=False, has_headers=False):
        """
        Inicializa a classe TemplateProcessor com os parâmetros fornecidos.

        Args:
        - sheet: Planilha na qual os dados serão processados.
        - item: Item associado ao template.
        - cnt_row: Contador de linhas na planilha.
        - statement: Declaração associada ao template.
        - force (bool): Indica se a ação deve ser forçada (padrão é False).
        - has_headers (bool): Indica se há cabeçalhos na planilha (padrão é False).
        """
        self.index_order = {}
        self.sheet = sheet
        self.item = item
        self.cnt_row = cnt_row
        self.force = force
        self.has_headers = has_headers
        self.statement = statement

    def set_template(self):
        """
        Define o template na planilha.
        """
        template = self.item.template
        template_serializer = TemplateSchema(template).data

        for table in template_serializer['tables']:
            self._process_table(template_serializer, table)

    def _process_table(self, template, table):
        """
        Processa uma tabela específica do template.

        Args:
        - template: Template do item.
        - table: Tabela a ser processada.
        """

        nested_attrs = []
        template_name = self.item.template.name
        color = gray_fill
        font = bold_font
        unique_headers = False
        summary = sorted(table['summary'], key=lambda x: x['order'])

        if table['slug'] == TemplateSlugChoices.FUNDS:
            fund_items = self.item.get_all_statement_funds()
            total_funds = self.item.get_total_values_funds()
        elif table['slug'] == TemplateSlugChoices.FUNDS_INTEGRATION:
            fund_items = self.item.get_all_statement_funds_integrations()
            total_funds = self.item.get_total_values_funds_integrations()
            template_name = f'Integrações sobre {self.item.template.name}'
        elif table['slug'] == TemplateSlugChoices.DOCUMENT:
            fund_item = self.item.get_statement()
            fund_items = [fund_item]
            nested_attrs = [self.item.get_total_funds()]
            total_funds = self.statement.get_statement_pj()
            color = green_fill
            font = bold_white_font
            unique_headers = True
        elif table['slug'] == TemplateSlugChoices.Danos:
            fund_item = self.item.get_statement()
            fund_items = [fund_item]
            total_obj = self.item.get_total_funds()
            total_funds = [total_obj, fund_item]
            nested_attrs = [total_obj]
            unique_headers = True
        else:
            msg = 'Table não mapeada na geração do extrato contábil'
            logging.error(msg)
            raise ValueError(msg)

        if not unique_headers:
            set_sheet_value(self.sheet, self.cnt_row + 1, 'A',
                            template_name, font=bold_font)
            self.cnt_row += 1

        self._process_fields(table, fund_items, nested_attrs,
                             color, font, unique_headers)
        self._process_summary(summary, total_funds)
        self.cnt_row += 2

    def _process_fields(self, table, fund_items, nested_attrs, color, fonte, unique_headers):
        """
        Processa os campos da tabela.

        Args:
        - table: Tabela a ser processada.
        - fund_items: Items de verbas associados.
        - nested_attrs: Atributos aninhados.
        - color: Cor a ser utilizada.
        - fonte: Fonte a ser utilizada.
        - unique_headers (bool): Indica se os cabeçalhos são únicos.
        """
        letter = 'A'
        fields = sorted(table['fields'], key=lambda x: x['order'])
        self.cnt_row += 1

        for field in fields:
            key = field['key']
            if key == 'status_display':
                continue
            if not unique_headers or not self.has_headers:
                set_sheet_value(self.sheet, self.cnt_row, letter,
                                field['label'], font=fonte, fill=color)

            self.index_order[field['order']] = letter
            letter = chr(ord(letter) + 1)

            if not fund_items:
                set_sheet_value(self.sheet, self.cnt_row + 1, letter, '-')
        self.has_headers = True

        self.cnt_row += 1
        if fund_items:
            for index, fund_item in enumerate(fund_items):

                if self.force:
                    set_sheet_value(self.sheet, self.cnt_row,
                                    letter, '', force=self.force)
                for field in fields:
                    key = field['key']
                    if key == 'status_display':
                        continue

                    value = get_nesteds_attr(nested_attrs + [fund_item], key)
                    type_value = field['type']
                    value = self._get_formatted_value(type_value, value)

                    letter = self.index_order[field['order']]
                    if type_value == FieldTypeChoices.FLOAT:
                        set_sheet_number(
                            self.sheet, self.cnt_row, letter, value)
                    else:
                        set_sheet_value(
                            self.sheet, self.cnt_row, letter, value)

                if index < len(fund_items) - 1:
                    self.cnt_row += 1

    def _get_formatted_value(self, type_value, value):
        """
        Formata o valor com base no tipo de campo.

        Args:
        - type_value: Tipo do campo.
        - value: Valor a ser formatado.

        Returns:
        - str: Valor formatado.
        """
        if type_value == FieldTypeChoices.DATE:
            if value:
                return datetime.strftime(value, "%d/%m/%Y")
            return '-'
        elif type_value == FieldTypeChoices.DATETIME:
            return datetime.strftime(value, "%d/%m/%Y %H:%M:%S")
        elif type_value == FieldTypeChoices.BOOLEAN:
            return 'Sim' if value else 'Não'
        return value if value is not None else '-'

    def _process_summary(self, summary, total_funds):
        """
        Processa o resumo da tabela.

        Args:
        - summary: Fields de resultado a ser processado.
        - total_funds: O objeto para ser extraídos os valores.
        """
        for summ in summary:
            key = summ.get('key')
            order = summ.get('order')

            if key and str(key).lower() != 'none':

                if isinstance(total_funds, list) is False:
                    nested_attrs = [total_funds]
                else:
                    nested_attrs = total_funds
                if nested_attrs:
                    value = get_nesteds_attr(nested_attrs, key)
                    if value is None:
                        value = '-'
                else:
                    value = '-'
            else:
                value = summ['label']

            val = self.index_order[order]

            if summ['type'] == FieldTypeChoices.FLOAT:
                set_sheet_number(self.sheet, self.cnt_row + 1,
                                 val, value, font=bold_font)
            else:
                set_sheet_value(self.sheet, self.cnt_row + 1,
                                val, value, font=bold_font)
