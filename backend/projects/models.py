import pickle
import re
import traceback
from datetime import datetime
import xlsxwriter

from django.db import models, transaction
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.utils.translation import activate, deactivate
from numpy import number
from rest_framework import serializers

from base.coins.models import COIN_CHOICES
from base.models import AbstractDateRecovering, AbstractDescription, CHOICES_REPRESENTATION_DOCUMENTATION, \
    CHOICES_CLAIM_TYPE, NATURE_CHOICES, NatureChoice
from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from calculation.models import Calculation, CHOICES_STEP
from core.entity.models import Entity
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
    def num_recovering(self) -> number:
        return self.recovering_set.all().count()

    def get_project_users(self):
        return self.engagement.users.all()

    def calc_by_step(self):
        """
        Returns a list of dictionaries containing the count of calculations for each status step (defined by `STATUS_CHOICES`)
        associated with the `Creditor` objects associated with the `Recovering` objects
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

    def get_valid_excels_headers(self):
        # enabling translation to output only in a single language and not generate errors in different languages
        activate('pt-br')

        default_columns = [
            {"title": "Credor", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Credor - CPF/CNPJ", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Credor - CPF/CNPJ da Recuperanda", 'choice': None, 'default': None, 'type': 'str'},
            {"title": "Credor - Nome da Recuperanda", 'choice': None, 'default': None, 'type': 'str'},

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
        rj_columns[4:4] = [
            {"title": "Pleito do Credor - Classe(Opcional)", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Pleito do Credor - Valor(Opcional)", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Pleito do Credor - Moeda(Opcional)", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Pleito do Credor - N° do Incidente(Opcional)", 'choice': None, 'default': None, 'type': 'str'},

            {"title": "Edital RJ - Class(Opcional)", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital RJ - Valor(Opcional)", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Edital RJ - Moeda(Opcional)", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital RJ - N° do Incidente(Opcional)", 'choice': None, 'default': None, 'type': 'str'},

        ]

        aj_columns = default_columns.copy()
        aj_columns[4:4] = [
            {"title": "Pleito do Credor - Classe(Opcional)", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Pleito do Credor - Valor(Opcional)", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Pleito do Credor - Moeda(Opcional)", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Pleito do Credor - N° do Incidente(Opcional)", 'choice': None, 'default': None, 'type': 'str'},

            {"title": "Edital AJ - Classe(Opcional)", 'choice': CLASSE_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital AJ - Valor(Opcional)", 'choice': None, 'default': None, 'type': 'float'},
            {"title": "Edital AJ - Moeda(Opcional)", 'choice': COIN_CHOICES, 'default': None, 'type': 'str'},
            {"title": "Edital AJ - N° do Incidente(Opcional)", 'choice': None, 'default': None, 'type': 'str'},
        ]

        excels = [
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors', columns=default_columns),
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors_rj', columns=rj_columns),
            ExcelHeader(callback=self.process_json_to_model, name='create_creditors_aj', columns=aj_columns),
        ]

        deactivate()
        return excels

    def parse_file(self, file_obj):
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
            raise serializers.ValidationError(_('Excel is not in the correct format'))

    def process_json_to_model(self, data: list, **kwargs):
        from recovering.schemas import RecoveringSchema
        from calculation.schemas import IncidentSchema

        name = kwargs.get('name')
        excel = self.get_excel_by_name(name)
        data = excel.parse_list(data)
        all_natures = NatureChoice.objects.all()
        file_id = kwargs.get('file_id')

        if not data:
            ErrorFile.objects.create(file_id=file_id, error='A lista de excel processada estava vazia')
            return

        recoveries = self.recovering_set.all().values('id', 'entity__legal_number')
        for credor in data:
            try:
                with transaction.atomic():
                    natures = []
                    nature = credor['Natureza (NF, contrato, trabalhista etc)']
                    recovering_legal_number = ''.join(
                        re.findall(r'\d', str(credor['Credor - CPF/CNPJ da Recuperanda'])))

                    recovering_name = str(credor['Credor - Nome da Recuperanda'])

                    recovering = None
                    for rec in recoveries:
                        if rec['entity__legal_number'] == recovering_legal_number:
                            recovering = rec['id']
                            break

                    if not recovering:
                        recovering_data = {
                            "entity": {
                                "name": recovering_name,
                                "legal_number": recovering_legal_number
                            },
                            "project_id": self.id,
                        }
                        recovering_schema = RecoveringSchema(data=recovering_data)
                        is_valid = recovering_schema.is_valid(raise_exception=False)

                        if not is_valid:
                            ErrorFile.objects.create(file_id=file_id,
                                                     error=f'Linha: {credor["index"]}, {recovering_schema.errors}')
                            continue
                        recovering = recovering_schema.save()

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

                    claim_classe = credor.get('Pleito do Credor - Classe(Opcional)')
                    claim_coin = credor.get('Pleito do Credor - Moeda(Opcional)')
                    claim_value = credor.get('Pleito do Credor - Valor(Opcional)')
                    claim_incident = credor.get('Pleito do Credor - N° do Incidente(Opcional)')
                    if all([claim_classe, claim_coin]) and claim_value is not None:

                        incident_schema = IncidentSchema(data={'number': claim_incident})
                        is_valid = incident_schema.is_valid(raise_exception=False)

                        if not is_valid:
                            ErrorFile.objects.create(file_id=file_id,
                                                     error=f'Linha: {credor["index"]}, {incident_schema.errors}')
                            continue
                        incident = incident_schema.save()

                        claims_creditor.append({
                            "classes": {
                                "classe": claim_classe
                            },
                            "coins": {
                                "coin": claim_coin,
                                "value": claim_value
                            },
                            "incident_id": incident.id,
                        })

                    notice_rj_classe = credor.get('Edital RJ - Class(Opcional)')
                    notice_rj_coin = credor.get('Edital RJ - Moeda(Opcional)')
                    notice_rj_value = credor.get('Edital RJ - Valor(Opcional)')
                    notice_rj_incident = credor.get('Edital RJ - N° do Incidente(Opcional)')
                    if all([notice_rj_classe, notice_rj_coin]) and notice_rj_value is not None:

                        incident_schema = IncidentSchema(data={'number': notice_rj_incident})
                        is_valid = incident_schema.is_valid(raise_exception=False)

                        if not is_valid:
                            ErrorFile.objects.create(file_id=file_id,
                                                     error=f'Linha: {credor["index"]}, {incident_schema.errors}')
                            continue
                        incident = incident_schema.save()

                        notice_rj_creditor.append({
                            "classes": {
                                "classe": notice_rj_classe
                            },
                            "coins": {
                                "coin": notice_rj_coin,
                                "value": notice_rj_value
                            },
                            "incident_id": incident.id,
                        })

                    notice_aj_classe = credor.get('Edital AJ - Classe(Opcional)')
                    notice_aj_coin = credor.get('Edital AJ - Moeda(Opcional)')
                    notice_aj_value = credor.get('Edital AJ - Valor(Opcional)')
                    notice_aj_incident = credor.get('Edital AJ - N° do Incidente(Opcional)')
                    if all([notice_aj_classe, notice_aj_coin]) and notice_aj_value is not None:

                        incident_schema = IncidentSchema(data={'number': notice_aj_incident})
                        is_valid = incident_schema.is_valid(raise_exception=False)

                        if not is_valid:
                            ErrorFile.objects.create(file_id=file_id,
                                                     error=f'Linha: {credor["index"]}, {incident_schema.errors}')
                            continue
                        incident = incident_schema.save()

                        notice_aj_creditor.append({
                            "classes": {
                                "classe": notice_aj_classe
                            },
                            "coins": {
                                "coin": notice_aj_coin,
                                "value": notice_aj_value
                            },
                            "incident_id": incident.id,
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
                print(e, 'err proccess file\n')
                traceback.print_exc()  # Imprime o traceback completo no console
                ErrorFile.objects.create(file_id=file_id, error=str(e), status='P')


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
