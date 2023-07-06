import pickle
import xlsxwriter

from django.db import models
from django.db.models import Count, Sum
from numpy import number

from base.coins.models import COIN_CHOICES
from base.models import AbstractDateRecovering, AbstractDescription, SELECT_CHOICES_REPRESENTATION_DOCUMENTATION, \
    SELECT_CHOICES_CLAIM_TYPE, CHOICES_REPRESENTATION_DOCUMENTATION, CHOICES_CLAIM_TYPE, NATURE_CHOICES
from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from calculation.models import Calculation, CHOICES_STEP
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import Creditor
from file.tasks import ProcessExcelTask, SaveFileTask
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
    def num_recovering(self) -> number:
        return self.recovering_set.all().count()

    def get_project_users(self):
        return self.engagement.users.all()

    def calc_by_step(self):
        """
        Returns a list of dictionaries containing the count of calculations for each status step (defined by `STATUS_CHOICES`)
        associated with the `Creditor` objects associated with the `Recovering` objects
        that are associated with this `Project` object.

        Returns:
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
        print(step_counts, 'step counts\n')
        return step_counts

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_sum_creditors = None

    def total_sum_creditors(self) -> float:
        total = Creditor.objects.filter(recovering__project=self).select_related('recovering__project').aggregate(
            Sum('total'))['total__sum']
        return total if total else 0

    def total_historical_sum_creditors(self) -> float:
        total = Creditor.objects.filter(recovering__project=self).select_related('recovering__project').aggregate(
            Sum('total_historical'))['total_historical__sum']
        return total if total else 0

    def total_creditor(self):
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

    def get_excel_by_name(self, name):
        for obj in self.get_valid_excels_headers():
            if obj.get_name() == name:
                return obj
        return None

    def get_valid_excels_headers(self):
        return [
            ExcelHeader(callback=self.process_json_to_model,
                        name='create_creditors_claim',
                        columns=[
                            {"title": "Credor", 'choice': None},
                            {"title": "Credor - CPF/CNPJ", 'choice': None},
                            {"title": "Credor - Classe", 'choice': CLASSE_CHOICES},
                            {"title": "Credor - Valor", 'choice': None},
                            {"title": "Credor - Moeda", 'choice': COIN_CHOICES},
                            {"title": "Credor - Recuperanda CPF/CNPJ", 'choice': None},
                            {"title": "Documentação de representação", 'choice': CHOICES_REPRESENTATION_DOCUMENTATION},
                            {"title": "Tipo", 'choice': CHOICES_CLAIM_TYPE},
                            {"title": "Natureza (NF, contrato, trabalhista etc)", 'choice': NATURE_CHOICES},
                            {"title": "Descrição", 'choice': None},
                            {"title": "Status", 'choice': SELECT_CHOICES_REPRESENTATION_DOCUMENTATION},
                            {"title": "Prazo resposta", 'choice': None},
                        ]
                        )
        ]

    def parse_file(self, file_obj):
        file_read, file_excel_headers = file_obj.get_excel_headers()
        headers_excels = self.get_valid_excels_headers()

        for excel in headers_excels:
            equal_headers = excel.compare_headers(file_excel_headers)
            print(equal_headers, 'equal_headers\n')
            if equal_headers:
                funcao_serializada = pickle.dumps(excel.get_callback())
                task = ProcessExcelTask.delay('task-process-excel-to-json', file_read, funcao_serializada)
                SaveFileTask.delay(task.id, file_obj.id)
                break

    def generate_excel_example_ok(self):
        workbook = xlsxwriter.Workbook('planilha_excel.xlsx')
        worksheet = workbook.add_worksheet()
        headers = ["Credor", "Credor - CPF/CNPJ", "Credor - Classe", "Credor - Valor", "Credor - Moeda"]
        min_row = 1
        max_row = 1048575
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)
            if header == "Credor - Classe":
                worksheet.data_validation(min_row, i, max_row, i,
                                          {'validate': 'list',
                                           'source': [choice[1] for choice in CLASSE_CHOICES],
                                           'input_title': 'Selecione uma opção',
                                           'input_message': 'Escolha uma opção da lista.'})
        workbook.close()

    def process_json_to_model(self, data: list):
        name = 'create_creditors_claim'
        # Creditor.objects.create
        print(data, 'data received\n\n')
        excel = self.get_excel_by_name(name)
        data = excel.parse_list(data)
        for credor in data:
            print(credor, 'new_keys_creditor')
            # # Creditor.objects.create(**credor) # TODO: criar logica de criacao aqui

            new_credor = {
                "entity": {
                    "name": credor['Credor'],
                    "legal_number": credor['Credor - CPF/CNPJ']
                },
                "claim_creditor": [
                    {
                        "classes": {
                            "classe": credor['Credor - Classe']
                        },
                        "coins": {
                            "coin": credor['Credor - Moeda'],
                            "value": credor['Credor - Valor']
                        },
                    }
                ],
            }
            print(new_credor)
            # TODO: subir credor inativo. Ter tela/endpoint pra aprovar credor


class ExcelHeader:
    def __init__(self, callback, name, columns):
        self._callback = callback
        self._name = name
        self._columns = columns

    def get_column_titles(self):
        return [column["title"] for column in self._columns]

    def compare_headers(self, excel_headers: list):
        headers = set(self.get_column_titles())
        return set(excel_headers) == headers

    def get_callback(self):
        return self._callback

    def get_columns(self):
        return self._columns

    def get_name(self):
        return self._name

    def parse_list(self, data):
        new_data = []
        for credor in data:
            print(credor, 'new_keys_creditor')
            columns = self.get_columns()
            new_credor = {}
            for column in columns:
                choice = column.get('choice')
                title = column.get('title')

                if choice:
                    new_credor[title] = get_first_value(choice, credor[title])
                else:
                    new_credor = credor[title]

                new_data.append(new_credor)

        return new_data
