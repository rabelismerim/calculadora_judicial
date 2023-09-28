import pickle
import re
import traceback
from datetime import datetime
import xlsxwriter

from django.db import models
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.utils.translation import activate, deactivate
from rest_framework import serializers

from base.coins.models import COIN_CHOICES
from base.models import AbstractDateRecovering, AbstractDescription, CHOICES_REPRESENTATION_DOCUMENTATION, \
    CHOICES_CLAIM_TYPE, NATURE_CHOICES, NatureChoice
from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from calculation.models import Calculation, CHOICES_STEP
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import Creditor, CHOICES_STATUS_LEGAL
from file.models import ErrorFile
from file.tasks import ProcessExcelTask
from projects.court.models import Court
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.region.models import Region
from projects.engagement.models import ProjectEngagement
from utils import get_user_model, _

User = get_user_model()
STATUS_CHOICES = (
    ('E', _('In preparation')),
    ('C', _('Concluded')),
    ('A', _('In progress')),
    ('F', _('Canceled')),
)

CHOICES_PHYSICAL_PERSON = (('verdadeiro', 'verdadeiro'), ('falso', 'falso'))


def get_first_value(choices, second_value):
    for choice in choices:
        if choice[1] == second_value:
            return choice[0]
    return None


class Project(AbstractDescription, AbstractDateRecovering):
    """
    This class Project represents a grand project/engagement.
    It contains the properties project_start and project_end for specifying the start and end date of the project, 
    as well as a status field with choices specified by the constant STATUS_CHOICES. 
    Additionally it stores relations to other models such as Judge, Lawyer, and Region through foreign keys,
    as well as a one-to-one relationship to the model ProjectEngagement through the field engagement. 
    Lastly it has two fields containing relationships to the User model, namely manager and partner. 
    The property num_recovering is responsible for retrieving the number of recovering related to this project. 
    Lastly the string representation of this object is defined in the method __str__.
    """

    project_start = models.DateField(null=True, blank=True)
    project_end = models.DateField(null=True, blank=True)
    process_number = models.CharField(_("Process number"), max_length=25)

    status = models.CharField(default="E", max_length=1, choices=STATUS_CHOICES)
    is_adm = models.BooleanField(default=True)  # É administrativa ou judicial
    judge = models.ForeignKey(Judge, on_delete=models.PROTECT)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    court = models.ForeignKey(Court, on_delete=models.PROTECT)
    competence = models.CharField(_("Competence"), max_length=150, null=True)
    legal_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='legal_manager', null=True)  # Gerente jurídico
    calculation_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='calculation_manager', null=True)  # Gerente de calculos
    financial_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='financial_manager', null=True)  # Gerente Financeiro
    legal_partner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='legal_partner', null=True)  # Socio jurídico
    financial_partner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='financial_partner', null=True)  # Socio Financeiro
    engagement = models.OneToOneField(ProjectEngagement, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.description}"

    @property
    def num_recovering(self) -> int:
        """
        Retrieves the number of recoverings associated with the project.

        Returns:
            int: The number of recoverings.

        Notes:
            - The property uses the 'recovering_set' attribute to access the related Recovering objects.
            - It retrieves all the related Recovering objects using the 'all()' method.
            - It counts the number of Recovering objects and returns the count.

        """
        return self.recovering_set.all().count()

    def get_project_users(self):
        """
        Retrieves the users associated with the project.

        Returns:
            QuerySet: A queryset containing the users associated with the project.

        Notes:
            - The function uses the 'engagement' attribute to access the related Engagement object.
            - It retrieves all the related users using the 'users' attribute of the Engagement object.
            - It returns the queryset containing the users associated with the project.

        """
        return self.engagement.users.all()

    def calc_by_step(self) -> list:
        """
        Returns a list of dictionaries containing the count of calculations for each status step (defined by
        `STATUS_CHOICES`) associated with the `Creditor` objects associated with the `Recovering` objects
        that are associated with this `Project` object.

        :return:
            A list of dictionaries with the following keys:
                - 'total': the count of `Calculation` objects in the given status step
                - 'step': the status step
                - 'step_display': the display name for the status step
        """
        qs = Calculation.objects.filter(creditor__recovering__project=self).values('step').annotate(total=Count('id'))

        dict_choices = dict(CHOICES_STEP)
        step_counts = []
        for calc in qs:
            step_counts.append(
                {'total': calc['total'], 'step': calc['step'], 'step_display': dict_choices.get(calc['step'])})

        # Add steps with total count of 0
        existing_steps = set(x['step'] for x in step_counts)
        all_steps = set(x[0] for x in CHOICES_STEP)
        missing_steps = all_steps - existing_steps
        for step in missing_steps:
            step_counts.append({'total': 0, 'step': step, 'step_display': dict(CHOICES_STEP)[step]})
        return step_counts

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_sum_creditors = None

    def total_sum_creditors(self) -> float:
        """
        Calculates the total sum of creditors for the project.

        Returns:
            float: The total sum of creditors.

        Notes:
            - The function filters the Creditor objects based on the project.
            - It selects related Recovering objects to optimize the query.
            - It aggregates the 'total' field of the filtered Creditor objects and retrieves the sum.
            - If the sum is None, it returns 0.

        """
        total = Creditor.objects.filter(recovering__project=self).select_related('recovering__project').aggregate(
            Sum('total'))['total__sum']
        return total if total else 0

    def total_historical_sum_creditors(self) -> float:
        """
        Calculates the total historical sum of creditors for the project.

        Returns:
            float: The total historical sum of creditors.

        Notes:
            - The function filters the Creditor objects based on the project.
            - It selects related Recovering objects to optimize the query.
            - It aggregates the 'total_historical' field of the filtered Creditor objects and retrieves the sum.
            - If the sum is None, it returns 0.

        """
        total = Creditor.objects.filter(recovering__project=self).select_related('recovering__project').aggregate(
            Sum('total_historical'))['total_historical__sum']
        return total if total else 0

    def total_creditor(self) -> int:
        """
        Counts the total number of creditors for the project.

        Returns:
            int: The total number of creditors.

        Notes:
            - The function filters the Creditor objects based on the project.
            - It counts the number of filtered Creditor objects and returns the count.

        """
        return Creditor.objects.filter(recovering__project=self).count()

    def total_classes_creditor(self):
        classes = [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                    'coin': fund.coins.get_coin_display(),
                    'total_historical': fund.get_total_historical_summed(),
                    'total_calculated': fund.get_total_summed()} for fund in
                   Funds.objects.filter(classes__classe__isnull=False, calculation__creditor__recovering__project=self,
                                        calculation__validated=True, calculation__step='A')]
        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_historical': fund.get_total_historical_summed(),
                     'total_calculated': fund.get_total_summed()} for fund in
                    FundDocument.objects.filter(classes__classe__isnull=False, calculation__validated=True,
                                                calculation__step='A',
                                                calculation__creditor__recovering__project=self)]
        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_historical': 0,
                     'total_calculated': fund.get_total_summed()} for fund in
                    FundIRRF.objects.filter(classes__classe__isnull=False, calculation__validated=True,
                                            calculation__step='A',
                                            calculation__creditor__recovering__project=self)]

        class_totals = {}
        total_value_sum = 0
        total_calculated_sum = 0
        total_calculated_sum_historical = 0
        quantity_by_classes = []
        for class_dict in classes:
            class_name = class_dict['classe']
            quantity_by_classes.append(class_name)
            class_total_value = class_dict['total_value']
            class_total_calculated = class_dict['total_calculated']
            class_total_historical = class_dict['total_historical']
            total_value_sum += class_total_value
            total_calculated_sum += class_total_calculated
            total_calculated_sum_historical += class_total_historical
            if class_name not in class_totals:
                class_totals[class_name] = {'total_value': class_total_value,
                                            'coin': class_dict['coin'],
                                            'total_calculated': class_total_calculated,
                                            'total_historical': class_total_historical,
                                            }
            else:
                class_totals[class_name]['total_value'] += class_total_value
                class_totals[class_name]['total_calculated'] += class_total_calculated
                class_totals[class_name]['total_historical'] += class_total_historical
                class_totals[class_name]['coin'] = class_dict['coin']
        for class_dict in class_totals.values():
            total_calculated = class_dict['total_calculated']
            total_value = class_dict['total_value']
            class_dict['percentage_calculated'] = (
                                                          total_calculated / total_calculated_sum) * 100 if total_calculated_sum > 0 else 0
            class_dict['percentage_value'] = (total_value / total_value_sum) * 100 if total_value_sum > 0 else 0

        classes_list = []
        classes_list_included = []
        classes_choices = dict(CLASSE_CHOICES)

        for class_name, total in class_totals.items():
            obj = {'classe': class_name, 'classes_display': classes_choices.get(class_name),
                   'total_value': total['total_value'], 'total_calculated': total['total_calculated'],
                   'total_historical': total['total_historical'],
                   'coin': total.get('coin'),
                   'percentage_value': total.get('percentage_value', 0),
                   'quantity': quantity_by_classes.count(class_name),
                   'percentage_calculated': total.get('percentage_calculated', 0)}
            classes_list.append(obj)
            classes_list_included.append(class_name)
        for key, value in CLASSE_CHOICES:
            if not key in classes_list_included:
                obj = {'classe': key, 'classes_display': value,
                       'total_value': 0, 'total_calculated': 0,
                       'percentage_value': 0,
                       'total_historical': 0,
                       'quantity': 0,
                       'coin': '',
                       'percentage_calculated': 0}
                classes_list.append(obj)
        return classes_list

    def get_valid_excels_headers(self):
        """
        Retrieves a list of valid Excel headers configurations.

        Returns:
            list: A list of ExcelHeader objects representing valid Excel headers configurations.

        Notes:
            - The function enables translation to output only in a single language and not generate errors in different
            languages.
            - The returned list includes default columns and specific Excel headers configurations.

        ExcelHeader Attributes:
            - callback (function): The callback function to be executed when processing the Excel data.
            - name (str): The name of the Excel headers configuration.
            - columns (list): A list of dictionaries representing the columns in the Excel headers configuration.

        Column Dictionary Attributes:
            - title (str): The title of the column.
            - choice (None or list): Optional choices for the column.
            - default (None or any): Optional default value for the column.
            - type (str): The data type of the column.

        """
        # enabling translation to output only in a single language and not generate errors in different languages
        activate('pt-br')

        default_columns = [
            {"title": "Credor", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Credor - CPF/CNPJ", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Credor - Recuperanda CPF/CNPJ", 'choice': None, 'default': None, 'type': 'str'},

            {"title": "Documentação de representação", 'choice': CHOICES_REPRESENTATION_DOCUMENTATION,
             'default': None, 'type': 'str'},
            {"title": "Tipo", 'choice': CHOICES_CLAIM_TYPE, 'default': None, 'type': 'str'},
            {"title": "Natureza (NF, contrato, trabalhista etc)", 'choice': NATURE_CHOICES,
             'default': None, 'type': 'str'},
            {"title": "Descrição", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Status", 'choice': CHOICES_STATUS_LEGAL, 'default': None, 'type': 'str'},
            {"title": "Prazo resposta", 'choice': None, 'default': None, 'type': 'date'},
            {"title": "Pessoa Física", 'choice': CHOICES_PHYSICAL_PERSON, 'default': None,
             'type': 'str'},
        ]

        rj_columns = default_columns.copy()
        rj_columns[3:3] = [
            {"title": "Credor - Classe", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Credor - Valor", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Credor - Moeda", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},

            {"title": "Edital RJ - Classe", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital RJ - Valor", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Edital RJ - Moeda", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
        ]

        aj_columns = default_columns.copy()
        aj_columns[3:3] = [
            {"title": "Credor - Classe", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Credor - Valor", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Credor - Moeda", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},

            {"title": "Edital AJ - Classe", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital AJ - Valor", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Edital AJ - Moeda", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
        ]

        excels = [
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors', columns=default_columns),
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors_rj', columns=rj_columns),
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors_aj', columns=aj_columns),
        ]

        deactivate()
        return excels

    def parse_file(self, file_obj, raise_exception=True) -> tuple:
        """
        Parses the given file object and initiates a Celery task for processing.

        Args:
            file_obj: The file object to be parsed.
            raise_exception (bool): Whether to raise an exception if the file is not in the correct format. Default is True.

        Returns:
            tuple: A tuple containing a boolean indicating success or failure, and a message describing the result.

        Raises:
            serializers.ValidationError: If the file is not in the correct format and `raise_exception` is True.
        """
        file_id, file_read, file_excel_headers = file_obj.get_excel_headers()
        headers_excels = self.get_valid_excels_headers()
        has_excel = False
        for excel in headers_excels:
            equal_headers = excel.compare_headers(file_excel_headers)
            if equal_headers:
                funcao_serializada = pickle.dumps(excel.get_callback())
                task = ProcessExcelTask.delay('task-process-excel-to-json', file_read, funcao_serializada,
                                              **{'file_id': file_id, 'name': excel.get_name()})
                file_obj.task_id = task.id
                file_obj.save()
                has_excel = True
                break
        if not has_excel:
            msg = _('Excel is not in the correct format')
            if raise_exception:
                raise serializers.ValidationError(msg)
            return False, _('The file id {} Excel is not in the correct format').format(file_id)
        return True, _('The file id {} has been added for processing').format(file_id)

    def process_json_to_model(self, data: list, **kwargs):
        """
        Processes the given JSON data and creates creditor objects based on the provided Excel headers configuration.

        Args:
            data (list): The JSON data to be processed.
            **kwargs: Additional keyword arguments.
                - name (str): The name of the Excel headers configuration.
                - file_id (int): The ID of the file being processed.

        Notes:
            - The function retrieves the Excel headers configuration based on the provided name.
            - It parses the JSON data using the Excel headers configuration.
            - It retrieves all available nature choices.
            - It processes each creditor entry in the parsed data and creates creditor objects accordingly.
            - If any errors occur during processing, they are logged in the ErrorFile model.

        """
        name = kwargs.get('name')
        excel = self.get_excel_by_name(name)
        data = excel.parse_list(data)
        all_natures = NatureChoice.objects.all()
        file_id = kwargs.get('file_id')

        if not data:
            ErrorFile.objects.create(file_id=file_id, error='A lista de excel processada estava vazia')
            return
        for credor in data:
            try:
                natures = []
                nature = credor['Natureza (NF, contrato, trabalhista etc)']
                recovering_legal_number = ''.join(re.findall(r'\d', str(credor['Credor - Recuperanda CPF/CNPJ'])))
                recovering = self.recovering_set.filter(entity__legal_number=recovering_legal_number).values_list(
                    'id', flat=True).first()
                # recovering = self.recovering_set.filter().values_list('id', flat=True).first()
                if not recovering:
                    ErrorFile.objects.create(file_id=file_id,
                                             error=f'Linha: {credor["index"]}, Field recuperanda: Recuperanda não encontrada')
                    continue
                nature_id = all_natures.filter(
                    Q(description=nature) | Q(description_en=nature) | Q(description_pt_br=nature)).values_list(
                    'id',
                    flat=True).first()
                legal_pendencies = []
                credor_description = credor.get('Descrição')
                credor_description = credor_description if credor_description is not None \
                                                           and str(credor_description).strip() != '' else None

                if all([credor_description, credor.get('Status'), credor.get('Prazo resposta')]):
                    legal_pendencies.append(
                        {
                            "description": credor_description,
                            "status": credor['Status'],
                            "deadline": datetime.strptime(str(credor['Prazo resposta']), "%d/%m/%Y").date()
                        })

                if nature_id:
                    natures.append(nature_id)

                claims_creditor = []
                notice_rj_creditor = []
                notice_aj_creditor = []

                claim_classe = credor.get('Credor - Classe')
                claim_coin = credor.get('Credor - Moeda')
                claim_value = credor.get('Credor - Valor')
                if all([claim_classe, claim_coin]) and claim_value is not None:
                    claims_creditor.append({
                        "classes": {
                            "classe": claim_classe
                        },
                        "coins": {
                            "coin": claim_coin,
                            "value": claim_value
                        },
                    })

                notice_rj_classe = credor.get('Edital RJ - Classe')
                notice_rj_coin = credor.get('Edital RJ - Moeda')
                notice_rj_value = credor.get('Edital RJ - Valor')
                if all([notice_rj_classe, notice_rj_coin]) and notice_rj_value is not None:
                    notice_rj_creditor.append({
                        "classes": {
                            "classe": notice_rj_classe
                        },
                        "coins": {
                            "coin": notice_rj_coin,
                            "value": notice_rj_value
                        },
                    })

                notice_aj_classe = credor.get('Edital AJ - Classe')
                notice_aj_coin = credor.get('Edital AJ - Moeda')
                notice_aj_value = credor.get('Edital AJ - Valor')
                if all([notice_aj_classe, notice_aj_coin]) and notice_aj_value is not None:
                    notice_aj_creditor.append({
                        "classes": {
                            "classe": notice_aj_classe
                        },
                        "coins": {
                            "coin": notice_aj_coin,
                            "value": notice_aj_value
                        },
                    })

                new_credor = {
                    "entity": {
                        "name": credor['Credor'],
                        "legal_number": credor['Credor - CPF/CNPJ']
                    },
                    "recovering_id": recovering,
                    "claim_creditor": claims_creditor,
                    "notice_recovering": notice_rj_creditor,
                    "notice_aj": notice_aj_creditor,
                    "representation_documentation": credor['Documentação de representação'],
                    "claim_type": credor['Tipo'],
                    "physical_person": str(credor['Pessoa Física']).lower() in ['true', 'verdadeiro'],
                    "natures": natures,
                    "legal_pendencies": legal_pendencies,
                    "is_active": False,
                }

                from creditors.schemas import CreditorBulkSchema
                from creditors.views import CreateCreditor

                serializer = CreditorBulkSchema(data=new_credor)

                if serializer.is_valid(raise_exception=False):
                    creditor = serializer.validated_data
                    CreateCreditor().create_creditor(creditor)
                else:
                    for field, error_messages in serializer.errors.items():
                        for error_message in error_messages:
                            ErrorFile.objects.create(file_id=file_id,
                                                     error=f"Linha: {credor['index']}, Field {field}: {error_message}")

            except Exception as e:
                print(e, 'err process file\n')
                traceback.print_exc()  # Imprime o traceback completo no console
                ErrorFile.objects.create(file_id=file_id, error=str(e), status='P')


class ExcelHeader:
    """
    Represents an Excel headers configuration.

    Args:
        callback (function): The callback function to be executed when processing the Excel data.
        name (str): The name of the Excel headers configuration.
        columns (list): A list of dictionaries representing the columns in the Excel headers configuration.

    Attributes:
        _callback (function): The callback function to be executed when processing the Excel data.
        _name (str): The name of the Excel headers configuration.
        _columns (list): A list of dictionaries representing the columns in the Excel headers configuration.

    """

    def __init__(self, callback, name, columns):
        self._callback = callback
        self._name = name
        self._columns = columns

    def get_column_titles(self) -> list:
        """
        Retrieves the titles of the columns in the Excel headers configuration.

        Returns:
            list: A list of column titles.

        """
        return [column["title"] for column in self._columns]

    def compare_headers(self, excel_headers: list) -> bool:
        """
        Compares the provided Excel headers with the column titles in the Excel headers configuration.

        Args:
            excel_headers (list): The Excel headers to compare.

        Returns:
            bool: True if the Excel headers match the column titles, False otherwise.

        """
        headers = set(self.get_column_titles())
        return set(excel_headers) == headers

    def get_callback(self):
        """
        Retrieves the callback function associated with the Excel headers configuration.

        Returns:
           function: The callback function.

        """
        return self._callback

    def get_columns(self):
        """
        Retrieves the columns in the Excel headers configuration.

        Returns:
            list: A list of dictionaries representing the columns.

        """
        return self._columns

    def get_name(self):
        """
        Retrieves the name of the Excel headers configuration.

        Returns:
            str: The name of the Excel headers configuration.

        """
        return self._name

    def parse_list(self, data):
        """
        Parses the given list of data based on the Excel headers configuration.

        Args:
            data (list): The list of data to be parsed.

        Returns:
            list: A new list of parsed data.

        Notes:
            - The function retrieves the columns from the Excel headers configuration.
            - It iterates over each entry in the provided data and creates a new entry with the parsed values.
            - If a column has a choice defined, it retrieves the first value from the choices based on the original
            value.
            - If a column does not have a choice defined, it keeps the original value as is.
            - The function enables translation to output only in a single language and not generate errors in different
            languages.

        """
        new_data = []
        # enabling translation to output only in a single language and not generate errors in different languages
        activate('pt-br')
        for credor in data:
            columns = self.get_columns()
            new_credor = {'index': credor['index']}
            for column in columns:
                choice = column.get('choice')
                title = column.get('title')

                if choice:
                    new_credor[title] = get_first_value(choice, credor[title])
                else:
                    new_credor[title] = credor[title]

            new_data.append(new_credor)
        deactivate()
        return new_data

    def generate_excel_example(self):
        """
        Generates an example Excel file based on the Excel headers configuration.

        Returns:
            HttpResponse: An HTTP response containing the generated Excel file.

        Notes:
            - The function retrieves the name of the Excel headers configuration.
            - It creates an HTTP response with the content type set to 'application/ms-excel' and the filename based on
            the configuration name.
            - It creates a new workbook using the xlsxwriter library.
            - It adds a worksheet to the workbook.
            - It iterates over each column in the Excel headers configuration and performs the following actions:
                - Writes the column title to the first row of the worksheet.
                - If the column has choices defined, it adds data validation to the column and writes the first choice
                as the default value.
                - If the column has defaults defined, it writes the default value to the first row of the column.
                - If the column type is 'date', it sets the date format for the column and writes a sample date value.
                - Adjusts the column width based on the length of the title.
            - It closes the workbook.
            - The function enables translation to output only in a single language and not generate errors in different
            languages.

        """
        filename = self.get_name()
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'

        workbook = xlsxwriter.Workbook(response)
        # workbook = xlsxwriter.Workbook(f"{filename}.xlsx")
        worksheet = workbook.add_worksheet()
        headers = []
        min_row = 1
        max_row = 1048575
        # enabling translation to output only in a single language and not generate errors in different languages
        activate('pt-br')

        for index, columns in enumerate(self.get_columns()):
            title = columns['title']
            choices = columns['choice']
            defaults = columns['default']
            type_ = columns['type']
            headers.append(title)

            worksheet.write(0, index, title)
            if choices:
                worksheet.data_validation(min_row, index, max_row, index,
                                          {'validate': 'list',
                                           'source': [str(choice[1]) for choice in choices],
                                           'input_message': 'Escolha uma opção da lista.'
                                           })
                worksheet.write(min_row, index, str(choices[0][1]))
            if defaults:
                worksheet.write(min_row, index, str(defaults))

            if type_ == 'date':
                date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
                worksheet.write(min_row, index, '01/01/2022', date_format)

            worksheet.set_column(index, index, max(20, len(title)))
        workbook.close()
        deactivate()
        return response
