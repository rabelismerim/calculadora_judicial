import copy
import json

from django.core.management.base import BaseCommand

from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from rates.models import Template, TemplateField, TemplateRate, TemplateMainField, TemplateSummaryField, \
    TemplateMainSummaryField, TemplateMainFieldDefault, TemplateFieldDefault


def create_templates():
    """Create templates to rates"""
    fields_default_all = [{'label': 'Status', 'key': 'status_display', 'type': 'C', 'order': 15, 'is_editable': False,
                           'required': False},
                          ]

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
                      'default': False,
                      'required': True},
                     {'label': 'Data base', 'key': 'data_base', 'type': 'D', 'order': 4, 'is_editable': True,
                      'required': True},
                     {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 5,
                      'is_editable': True,
                      'required': True},
                     {'label': 'É extraconcursal', 'key': 'is_extraconcursal', 'type': 'B', 'order': 4,
                      'is_editable': True,
                      'default': False,
                      'required': True},
                     ]

    fund_irrf = [{'label': 'Nome da verba', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
                  'required': True},
                 {'label': 'Meses no período', 'key': 'months_period', 'type': 'I', 'order': 1,
                  'default': 1,
                  'is_editable': True,
                  'required': True},
                 {'label': 'É extraconcursal', 'key': 'is_extraconcursal', 'type': 'B', 'order': 4,
                  'is_editable': True,
                  'default': False,
                  'required': True},
                 ]

    fields_verbas = [{'label': 'Data base', 'key': 'data_base', 'type': 'D', 'order': 2, 'is_editable': True,
                      'required': True},

                     {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 6,
                      'is_editable': True,
                      'required': True},
                     {'label': 'Índice na data base', 'key': 'monetary_correction.index_data_base', 'type': 'F',
                      'order': 7,

                      'is_editable': False, 'required': False},
                     {'label': 'Índice na recuperação', 'key': 'monetary_correction.index_recovering', 'type': 'F',
                      'order': 8,

                      'is_editable': False, 'required': False},
                     {'label': 'Valor corrigido', 'key': 'monetary_correction.corrected_value', 'type': 'F', 'order': 9,

                      'is_editable': False, 'required': False},
                     {'label': 'É extraconcursal', 'key': 'is_extraconcursal', 'type': 'B', 'order': 4,
                      'is_editable': True,
                      'default': False,
                      'required': True},
                     ]
    summary_fields_verbas = [{'label': 'Total: ', 'key': None, 'type': 'C', 'order': 2, 'is_editable': False,
                              'required': False},
                             {'label': '', 'key': 'total_historical', 'type': 'F', 'order': 6,
                              'is_editable': False,
                              'required': False},
                             {'label': '', 'key': 'total_corrected', 'type': 'F', 'order': 9,
                              'is_editable': False,
                              'required': False}
                             ]

    fields_verbas_document = [
        {'label': 'Data base', 'key': 'data_base', 'type': 'D', 'order': 2, 'is_editable': True,
         'required': True},

        {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 6,
         'is_editable': True,
         'required': True},
        {'label': 'Índice na data base', 'key': 'monetary_correction.index_data_base', 'type': 'F',
         'order': 7,

         'is_editable': False, 'required': False},
        {'label': 'Índice na recuperação', 'key': 'monetary_correction.index_recovering', 'type': 'F',
         'order': 8,

         'is_editable': False, 'required': False},
        {'label': 'Valor corrigido', 'key': 'monetary_correction.corrected_value', 'type': 'F', 'order': 10,

         'is_editable': False, 'required': False},
        {'label': 'É extraconcursal', 'key': 'is_extraconcursal', 'type': 'B', 'order': 4,
         'is_editable': True,
         'default': False,
         'required': True},

        {'label': 'Documento', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
         'required': True},
        {'label': 'Número', 'key': 'number', 'type': 'C', 'order': 1, 'is_editable': True,
         'required': True},
        {'label': 'Dias', 'key': 'total_days', 'type': 'I', 'order': 9, 'is_editable': False,
         'required': False},
        {'label': 'Juros', 'key': 'total_default_interest', 'type': 'F', 'order': 11, 'is_editable': False,

         'required': False},
        {'label': 'Multa', 'key': 'total_fine', 'type': 'F', 'order': 12, 'is_editable': False,
         'required': False},
        {'label': 'Total devido', 'key': 'total_due', 'type': 'F', 'order': 13, 'is_editable': False,

         'required': False},
    ]

    summary_fields_document = [{'label': 'Total: ', 'key': 'none', 'type': 'C', 'order': 0, 'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_historical', 'type': 'F', 'order': 5,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_corrected', 'type': 'F', 'order': 10,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_days', 'type': 'I', 'order': 9,
                                'is_editable': False,
                                'required': False},

                               {'label': '', 'key': 'total_default_interest', 'type': 'F', 'order': 11,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_fine', 'type': 'F', 'order': 12,
                                'is_editable': False,
                                'required': False},
                               {'label': '', 'key': 'total_due', 'type': 'F', 'order': 13,
                                'is_editable': False,
                                'required': False},
                               ]

    fields_verbas.append({'label': 'Súmula 381', 'key': 'summary', 'type': 'B', 'order': 3, 'is_editable': True,
                          'default': False,
                          'required': True})
    summary_fields_verbas_integrations = copy.deepcopy(summary_fields_verbas)
    fields_verbas_reflexos = copy.deepcopy(fields_verbas)
    summary_fields_verbas_reflexos = copy.deepcopy(summary_fields_verbas)
    fields_verbas_reflexos.append({'label': 'Reflexos DSR ', 'key': 'dsr_reflexes', 'type': 'F', 'order': 5,
                                   'is_editable': True, 'required': True})
    summary_fields_verbas_reflexos.append({'label': '', 'key': 'total_dsr_reflexes', 'type': 'F', 'order': 5,

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
        {'label': 'Status', 'key': 'status_display', 'type': 'C', 'order': 6, 'is_editable': False,
         'required': False},
    ]

    summary_main_fields = [
        {'label': '', 'key': 'classes.classe_display', 'type': 'C', 'order': 0,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'coins.coin_display', 'type': 'C', 'order': 1,
         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'coins.value', 'type': 'F', 'order': 2,

         'is_editable': False,
         'required': False},
        {'label': '', 'key': 'rate.index', 'type': 'C', 'order': 3,
         'is_editable': False,
         'required': False},
    ]

    summary_main_fields_verbas_irrf_integrations = summary_main_fields.copy()
    summary_main_fields_verbas_irrf_integrations.extend([
        {'label': 'R$', 'key': 'total', 'type': 'F', 'order': 4, 'is_editable': False,

         'required': False},
    ])

    summary_main_fields_docs = [
        {'label': 'R$', 'key': 'total.total_corrected', 'type': 'F', 'order': 4, 'is_editable': False,

         'required': False}
    ]

    templates = [{'name': f'Documentos', 'description': f'Documento',
                  'fund_main': fund_document,
                  'end_point': '/juca/api/v1/calculation/funds/documents/detail/',
                  'end_point_main': '/juca/api/v1/calculation/funds/documents/',
                  'many': False,
                  'has_commit': True,
                  'summary_fields': summary_fields_document,
                  'summary_main_fields': summary_main_fields_docs,
                  'fields': fields_verbas_document},
                 {'name': f'Acordos', 'description': f'Acordo',
                  'fund_main': fund_document,
                  'end_point': '/juca/api/v1/calculation/funds/documents/detail/',
                  'end_point_main': '/juca/api/v1/calculation/funds/documents/',
                  'many': False,
                  'has_commit': True,
                  'summary_fields': summary_fields_document,
                  'summary_main_fields': summary_main_fields_docs,
                  'fields': fields_verbas_document}
                 ]
    # verbas = ['TST', 'TST.IPCA-E', 'IPCA-E', 'SELIC', 'IGP-M', 'INPC', 'IPCA', 'IGP-DI', 'IPC-FIPE', 'TJSP']
    verbas = ['Verbas']

    for verba in verbas:
        template = [
            {'name': f'{verba}', 'description': f'{verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'has_commit': True,
             'summary_fields': summary_fields_verbas,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas},
            {'name': f'{verba}', 'description': f'Integrações sobre {verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'has_commit': True,
             'summary_fields': summary_fields_verbas_integrations,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} + Reflexos', 'description': f'{verba} + Reflexos',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'has_commit': True,
             'summary_fields': summary_fields_verbas,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas_reflexos},
            {'name': f'{verba} + Reflexos', 'description': f'Integrações sobre {verba}',
             'end_point': '/juca/api/v1/calculation/funds/labor/integrations/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'has_commit': True,
             'summary_fields': summary_fields_verbas_integrations,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas_integrations},

            {'name': f'{verba} rescisórias', 'description': f'{verba} rescisórias',
             'end_point': '/juca/api/v1/calculation/funds/labor/',
             'fund_main': fund_labor,
             'end_point_main': '/juca/api/v1/calculation/funds/',
             'many': True,
             'has_commit': True,
             'summary_fields': summary_fields_verbas,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas},

            {'name': f'IRRF', 'description': f'Base de cálculo',
             'end_point_main': '/juca/api/v1/calculation/funds/irrf/',
             'is_horizontal': False,
             'fund_main': fund_irrf,
             'end_point': '/juca/api/v1/calculation/funds/irrf/labor/',
             'many': True,
             'has_commit': False,
             'summary_fields': summary_fields_irrf,
             'summary_main_fields': summary_main_fields_verbas_irrf_integrations,
             'fields': fields_verbas_irrf},

        ]
        templates.extend(template)

    # ab = TemplateRate.objects.filter(end_point='/juca/api/v1/calculation/funds/documents/').update(end_point='/juca/api/v1/calculation/funds/documents/detail/')
    # print(ab)
    # return
    for template in templates:
        fields = template.pop('fields')
        name = template.pop('name')
        end_point = template.pop('end_point_main')
        fund_main = template.pop('fund_main')
        summary_fields = template.pop('summary_fields')
        has_commit = template.pop('has_commit')
        summary_main_fields = template.pop('summary_main_fields')
        defaults = {'name': name, 'end_point': end_point}
        filters = {'name': name}
        new_template, created = Template.objects.get_or_create(defaults=defaults, **filters)

        if created is False:
            TemplateMainFieldDefault.objects.filter(field__template=new_template).delete()
            TemplateMainField.objects.filter(template=new_template).delete()

        for fund_ in fund_main:
            fund = fund_.copy()
            field_default = fund.pop('default', None)
            main, created = TemplateMainField.objects.get_or_create(template=new_template, **fund)
            if field_default is not None:
                has_default = TemplateMainFieldDefault.objects.filter(field=main, label=field_default).exists()
                if not has_default:
                    default_obj = TemplateMainFieldDefault(field_id=main.id, label=str(field_default),
                                                           value=json.dumps({'data': field_default}))
                    default_obj.save()
        for fund in summary_main_fields:
            defaults = fund.copy()
            defaults['template'] = new_template
            TemplateMainSummaryField.objects.get_or_create(defaults=defaults, **defaults)
        new_template_rate, created = TemplateRate.objects.get_or_create(template=new_template, **template)
        new_template_rate.has_commit = has_commit
        new_template_rate.save()
        if created is False:
            TemplateFieldDefault.objects.filter(field__rate=new_template_rate).delete()
            TemplateField.objects.filter(rate=new_template_rate).delete()
            TemplateSummaryField.objects.filter(rate=new_template_rate).delete()

        for field in fields:
            defaults = field.copy()
            field_default = defaults.pop('default', None)

            defaults['rate'] = new_template_rate

            main, created = TemplateField.objects.get_or_create(defaults=defaults, **defaults)

            if field_default is not None:
                has_default = TemplateFieldDefault.objects.filter(field=main, label=field_default).exists()
                if not has_default:
                    default_obj = TemplateFieldDefault(field_id=main.id, label=str(field_default),
                                                       value=json.dumps({'data': field_default}))
                    default_obj.save()
        for field in fields_default_all:
            defaults = field.copy()
            defaults['rate'] = new_template_rate
            TemplateField.objects.get_or_create(defaults=defaults, **defaults)
        for field in summary_fields:
            defaults = field.copy()
            defaults['rate'] = new_template_rate
            TemplateSummaryField.objects.get_or_create(defaults=defaults, **defaults)


def delete_verbas():
    templates = Template.objects.all()

    for x in templates:
        try:
            x.delete()
        except:
            pass


def correct_verbas():
    old_id = ['8503cfdb-d36d-45b8-a5fd-aefd330961e4']
    new_id = '48ed463e-8b3a-4029-b394-29e13f7dc951'
    Funds.objects.filter(template_id__in=old_id).update(template_id=new_id)
    FundDocument.objects.filter(template_id__in=old_id).update(template_id=new_id)
    FundIRRF.objects.filter(template_id__in=old_id).update(template_id=new_id)


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        create_templates()
        # correct_verbas()
        # delete_verbas()
