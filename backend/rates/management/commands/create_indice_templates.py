import copy

from django.core.management.base import BaseCommand

from rates.models import Template, TemplateField, TemplateRate, TemplateMainField, TemplateSummaryField, \
    TemplateMainSummaryField


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
                     {'label': 'Há multa adicional?', 'key': 'has_custom_fine', 'type': 'B', 'order': 3,
                      'is_editable': True,
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
                 {'label': 'Meses no período', 'key': 'months_period', 'type': 'I', 'order': 1,
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

    summary_fields_verbas = [{'label': 'Total: ', 'key': 'none', 'type': 'C', 'order': 0, 'is_editable': False,
                              'required': False},
                             {'label': '', 'key': 'total_historical', 'type': 'F', 'order': 5,
                              'is_editable': False,
                              'required': False},
                             {'label': '', 'key': 'total_corrected', 'type': 'F', 'order': 8,
                              'is_editable': False,
                              'required': False}
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

    summary_fields_document = [{'label': 'Total: ', 'key': 'none', 'type': 'C', 'order': 0, 'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_historical', 'type': 'F', 'order': 5,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_corrected', 'type': 'F', 'order': 8,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_days', 'type': 'F', 'order': 9,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'default_interest', 'type': 'F', 'order': 10,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_fine', 'type': 'F', 'order': 11,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_due', 'type': 'F', 'order': 11,
                                'is_editable': False,
                                'required': False},
                               ]

    fields_verbas.append({'label': 'Súmula 381', 'key': 'summary', 'type': 'B', 'order': 3, 'is_editable': True,
                          'required': True})
    summary_fields_verbas_integrations = copy.deepcopy(summary_fields_verbas)
    fields_verbas_reflexos = copy.deepcopy(fields_verbas)
    summary_fields_verbas_reflexos = copy.deepcopy(summary_fields_verbas)
    fields_verbas_reflexos.append({'label': 'Reflexos DSR ', 'key': 'dsr_reflexes', 'type': 'F', 'order': 4,
                                   'is_editable': True, 'required': True})
    summary_fields_verbas_reflexos.append({'label': '', 'key': 'total_dsr_reflexes', 'type': 'F', 'order': 4,
                                           'is_editable': False,
                                           'required': False}, )

    fields_verbas_integrations = copy.deepcopy(fields_verbas)
    fields_verbas_integrations.append(
        {'label': 'Descrição', 'key': 'description', 'type': 'C', 'order': 0, 'is_editable': True,
         'required': True})

    fields_verbas_irrf = [
        {'label': 'Verbas', 'key': 'fund_name', 'type': 'C', 'order': 0, 'is_editable': True,
         'required': True},
        {'label': 'Valores tributáveis', 'key': 'taxable_amounts', 'type': 'F', 'order': 1, 'is_editable': True,
         'required': True}
    ]

    summary_fields_irrf = [
        {'label': 'Valor tributável', 'key': 'taxable_amount', 'type': 'F', 'order': 0, 'is_editable': False,
         'required': False},
        {'label': '', 'key': 'taxable_portion', 'type': 'F', 'order': 1,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'aliquot', 'type': 'F', 'order': 2,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'installment_deducted', 'type': 'F', 'order': 3,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'irrf_per_month', 'type': 'F', 'order': 4,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'irrf_per_period', 'type': 'F', 'order': 5,
         'is_editable': False,
         'required': False},
    ]

    templates = [{'name': f'Documentos', 'description': f'Documento',
                  'fund_main': fund_document,
                  'end_point': '/juca/api/v1/calculation/funds/documents/detail/',
                  'end_point_main': '/juca/api/v1/calculation/funds/documents/',
                  'many': False,
                  'summary_fields': summary_fields_document,
                  'fields': fields_verbas_document},
                 {'name': f'Acordos', 'description': f'Acordo',
                  'fund_main': fund_document,
                  'end_point': '/juca/api/v1/calculation/funds/documents/detail/',
                  'end_point_main': '/juca/api/v1/calculation/funds/documents/',
                  'many': False,
                  'summary_fields': summary_fields_document,
                  'fields': fields_verbas_document}
                 ]
    verbas = ['TST', 'TST.IPCA-E', 'IPCA-E', 'SELIC', 'IGP-M', 'INPC', 'IPCA', 'IGP-DI', 'IPC-FIPE', 'TJSP']

    for verba in verbas:
        template = [
            {'name': f'{verba}', 'description': f'{verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'summary_fields': summary_fields_verbas,
             'fields': fields_verbas},
            {'name': f'{verba}', 'description': f'Integrações sobre {verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'summary_fields': summary_fields_verbas_integrations,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} + Reflexos', 'description': f'{verba} + Reflexos',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'summary_fields': summary_fields_verbas,
             'fields': fields_verbas_reflexos},
            {'name': f'{verba} + Reflexos', 'description': f'Integrações sobre {verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'summary_fields': summary_fields_verbas_integrations,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} rescisórias', 'description': f'Verbas rescisórias {verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'summary_fields': summary_fields_verbas,
             'fields': fields_verbas},

            {'name': f'IRRF - {verba}', 'description': f'Base de cálculo',
             'end_point': '/juca/api/v1/calculation/funds/irrf/',
             'is_horizontal': False,
             'fund_main': fund_irrf,
             'end_point_main': '/juca/api/v1/calculation/funds/irrf/labor/',
             'many': True,
             'summary_fields': summary_fields_irrf,
             'fields': fields_verbas_irrf},

        ]
        templates.extend(template)

    for template in templates:
        fields = template.pop('fields')
        name = template.pop('name')
        end_point = template.pop('end_point_main')
        fund_main = template.pop('fund_main')
        summary_fields = template.pop('summary_fields')
        defaults = {'name': name, 'end_point': end_point}
        filters = {'name': name}
        new_template, created = Template.objects.get_or_create(defaults=defaults, **filters)

        if created is False:
            TemplateMainField.objects.filter(template=new_template).delete()

        for fund in fund_main:
            TemplateMainField.objects.get_or_create(template=new_template, **fund)
        # for fund in summary_fields_verbas: # TODO create summary to template main
        #     TemplateMainSummaryField.objects.get_or_create(template=new_template, **fund)
        new_template_rate, created = TemplateRate.objects.get_or_create(template=new_template, **template)
        if created is False:
            TemplateField.objects.filter(rate=new_template_rate).delete()
            TemplateSummaryField.objects.filter(rate=new_template_rate).delete()

        for field in fields:
            TemplateField.objects.get_or_create(rate=new_template_rate, **field)
        for field in summary_fields:
            TemplateSummaryField.objects.get_or_create(rate=new_template_rate, **field)


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        create_templates()
