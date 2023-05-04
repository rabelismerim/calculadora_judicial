import copy

from django.core.management.base import BaseCommand

from rates.models import Template, TemplateField, TemplateRate, TemplateMainField


def create_templates():
    """Create templates to rates"""
    fund_labor = [{'label': 'Nome da verba', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
                  'required': True}]
    fund_document = [{'label': 'Nome da verba', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
                  'required': True},
                     {'label': 'Número do documento', 'key': 'number', 'type': 'C', 'order': 1,
                      'is_editable': True,
                      'required': True},
                     {'label': 'Multa', 'key': 'fine', 'type': 'F', 'order': 2, 'is_editable': True,
                      'required': True},
                     {'label': 'Há multa adicional?', 'key': 'has_custom_fine', 'type': 'B', 'order': 3, 'is_editable': True,
                      'required': True},
                     {'label': 'Data base', 'key': 'data_base', 'type': 'D', 'order': 4, 'is_editable': True,
                      'required': True},
                     {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 5,
                      'is_editable': True,
                      'required': True},
                     {'label': 'É extraconcursal', 'key': 'is_extraconcursal', 'type': 'B', 'order': 6,
                      'is_editable': True,
                      'required': True},
                     ]
    fund_irrf = [{'label': 'Nome da verba', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
                  'required': True},
                     {'label': 'Meses no período', 'key': 'months_period', 'type': 'F', 'order': 1,
                      'is_editable': True,
                      'required': True}
                     ]

    fields_verbas = [{'label': 'Data base', 'key': 'data_base', 'type': 'D', 'order': 2, 'is_editable': True,
                      'required': True},
                     {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 5,
                      'is_editable': True,
                      'required': True},
                     {'label': 'Índice na data base', 'key': 'index_data_base', 'type': 'F', 'order': 6,
                      'is_editable': False, 'required': False},
                     {'label': 'Índice na recuperação', 'key': 'index_recovering', 'type': 'F', 'order': 7,
                      'is_editable': False, 'required': False},
                     {'label': 'Valor corrigido', 'key': 'corrected_value', 'type': 'F', 'order': 8,
                      'is_editable': False, 'required': False}
                     ]

    fields_verbas_document = copy.deepcopy(fields_verbas)
    fields_verbas_document.extend(
        [
            {'label': 'Documento', 'key': 'document', 'type': 'C', 'order': 0, 'is_editable': True,
             'required': True},
            {'label': 'Número', 'key': 'number', 'type': 'C', 'order': 1, 'is_editable': True,
             'required': True},
            {'label': 'Dias', 'key': 'days', 'type': 'I', 'order': 9, 'is_editable': False,
             'required': False},
            {'label': 'Juros', 'key': 'default_interest', 'type': 'F', 'order': 10, 'is_editable': False,
             'required': False},
            {'label': 'Multa', 'key': 'fine', 'type': 'F', 'order': 11, 'is_editable': False,
             'required': False},
            {'label': 'Total devido', 'key': 'total_due', 'type': 'F', 'order': 12, 'is_editable': False,
             'required': False},
        ])

    fields_verbas.append({'label': 'Súmula 381', 'key': 'summary', 'type': 'B', 'order': 3, 'is_editable': True,
                          'required': True})
    fields_verbas_integrations = copy.deepcopy(fields_verbas)
    fields_verbas_reflexos = copy.deepcopy(fields_verbas)
    fields_verbas_reflexos.append({'label': 'Reflexos DSR ', 'key': 'dsr_reflexes', 'type': 'F', 'order': 4,
                                   'is_editable': True, 'required': True})

    fields_verbas_integrations.append(
        {'label': 'Descrição', 'key': 'description', 'type': 'C', 'order': 0, 'is_editable': True,
         'required': True})

    fields_verbas_irrf = [
        {'label': 'Verbas', 'key': 'fund_name', 'type': 'C', 'order': 0, 'is_editable': True,
         'required': True},
        {'label': 'Valores tributáveis', 'key': 'taxable_amounts', 'type': 'F', 'order': 1, 'is_editable': True,
         'required': True}
    ]

    templates = [{'name': f'Documentos', 'description': f'Documento',
                  'fund_main': fund_document,
                  'end_point': '/djud/api/v1/calculation/funds/ducuments/',
                  'end_point_main': '/djud/api/v1/calculation/funds/ducuments/',
                  'many': False,
                  'fields': fields_verbas_document}, {'name': f'Acordos', 'description': f'Acordo',
                                                      'fund_main': fund_document,
                                                      'end_point': '/djud/api/v1/calculation/funds/ducuments/',
                                                      'end_point_main': '/djud/api/v1/calculation/funds/ducuments/',
                                                      'many': False,
                                                      'fields': fields_verbas_document}]
    verbas = ['TST', 'TST.IPCA-E', 'IPCA-E', 'SELIC', 'IGP-M', 'INPC', 'IPCA', 'IGP-DI', 'IPC-FIPE', 'TJSP']

    for verba in verbas:
        template = [
            {'name': f'{verba}', 'description': f'{verba}',
             'end_point': '/djud/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/djud/api/v1/calculation/funds/',
             'many': True,
             'fields': fields_verbas},
            {'name': f'{verba}', 'description': f'Integrações sobre {verba}',
             'end_point': '/djud/api/v1/calculation/funds/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/djud/api/v1/calculation/funds/',
             'many': True,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} + Reflexos', 'description': f'{verba} + Reflexos',
             'end_point': '/djud/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/djud/api/v1/calculation/funds/',
             'many': True,
             'fields': fields_verbas_reflexos},
            {'name': f'{verba} + Reflexos', 'description': f'Integrações sobre {verba}',
             'end_point': '/djud/api/v1/calculation/funds/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/djud/api/v1/calculation/funds/',
             'many': True,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} rescisórias', 'description': f'Verbas rescisórias {verba}',
             'end_point': '/djud/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/djud/api/v1/calculation/funds/',
             'many': True,
             'fields': fields_verbas},

            {'name': f'IRRF - {verba}', 'description': f'Base de cálculo',
             'end_point': '/djud/api/v1/calculation/funds/irrf/funds/',
             'fund_main': fund_irrf,
             'end_point_main': '/djud/api/v1/calculation/funds/irrf/',
             'many': True,
             'fields': fields_verbas_irrf},

        ]
        templates.extend(template)

    for template in templates:
        fields = template.pop('fields')
        name = template.pop('name')
        end_point = template.pop('end_point_main')
        fund_main = template.pop('fund_main')
        new_template, created = Template.objects.get_or_create(name=name, end_point=end_point)
        for fund in fund_main:
            TemplateMainField.objects.get_or_create(template=new_template, **fund)
        new_template_rate, created = TemplateRate.objects.get_or_create(template=new_template, **template)
        for field in fields:
            TemplateField.objects.get_or_create(rate=new_template_rate, **field)


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        create_templates()
