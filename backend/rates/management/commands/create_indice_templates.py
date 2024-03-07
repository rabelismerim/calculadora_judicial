import json

from calculation.funds.danos.models import InterestChoices
from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from django.core.management.base import BaseCommand
from rates.models import (FieldTypeChoices, Template, TemplateField,
                          TemplateFieldChoices, TemplateFieldDefault,
                          TemplateMainField, TemplateMainFieldChoices,
                          TemplateMainFieldDefault, TemplateMainSummaryField,
                          TemplateRate, TemplateSlugChoices,
                          TemplateSummaryField)

TEMPLATE_INSS = 'INSS'


def create_json(filename, data):
    with open(f'{filename}.json', 'w') as outfile:
        outfile.write(json.dumps(data, indent=4, default=str))

    fund_danos = [{'label': 'Nome da verba', 'key': 'name', 'type': 'C', 'order': 0, 'is_editable': True,
                   'required': True},
                  {'label': 'Descrição fato gerador', 'key': 'description', 'type': 'C', 'order': 1,
                   'is_editable': True,
                   'required': True},
                  {'label': 'Data da correção', 'key': 'data_base', 'type': 'D', 'order': 2, 'is_editable': True,
                   'required': True},
                  {'label': 'Tipo de juros', 'key': 'type_interest', 'type': FieldTypeChoices.CHOICES, 'order': 3,
                   'choices': InterestChoices.choices,
                   'is_editable': True,
                   'required': True},
                  {'label': 'Data Inicial do juros', 'key': 'interest_initial_date', 'type': 'D',
                   'order': 4,
                   'is_editable': True,
                   'required': False},
                  {'label': 'Valor histórico', 'key': 'historical_value', 'type': 'F', 'order': 5,
                   'is_editable': True,
                   'required': True},
                  {'label': 'Aplicar correção monetária?', 'key': 'apply_monetary_correction', 'type': 'B', 'order': 6,
                   'default': True, 'is_editable': True,
                   'required': False}
                  ]


class TemplateFundFront:
    available_templates = ['template_acordos', 'template_danos', 'template_document', 'template_irrf',
                           'template_verbas', 'template_verbas_integratorias', 'template_verbas_reflexos',
                           'template_verbas_rescisorias', 'template_deducao_due', 'template_deducao']

    # available_templates = ['template_deducao_due', 'template_deducao']

    def get_templates(self) -> list:

        templates = []

        for available in self.available_templates:
            template = open_json(f'rates/templates_frontend/{available}.json')
            templates.append(template)
        return templates

    def create_templates(self):
        """Create templates to rates"""
        fields_default_all = [
            {'label': 'Status', 'key': 'status_display', 'type': 'C', 'order': 15, 'is_editable': False,
             'required': False},
        ]
        templates = self.get_templates()

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
            new_template, created = Template.objects.get_or_create(
                defaults=defaults, **filters)

    # ab = TemplateRate.objects.filter(end_point='/juca/api/v1/calculation/funds/documents/').update(
    # end_point='/juca/api/v1/calculation/funds/documents/detail/') print(ab) return
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
        new_template, created = Template.objects.get_or_create(
            defaults=defaults, **filters)

        if created is False:
            TemplateMainFieldDefault.objects.filter(
                field__template=new_template).delete()
            TemplateMainField.objects.filter(template=new_template).delete()

        for fund_ in fund_main:
            fund = fund_.copy()
            field_default = fund.pop('default', None)
            field_choices = fund.pop('choices', None)
            main, created = TemplateMainField.objects.update_or_create(
                template=new_template, **fund)

            if field_choices is not None:
                field_choices = [{'id': str(choice[0]), 'legend': str(
                    choice[1])} for choice in field_choices]
                has_default = TemplateMainFieldChoices.objects.filter(field=main,
                                                                      choices=field_choices).exists()
                if not has_default:
                    default_obj = TemplateMainFieldChoices(
                        field_id=main.id, choices=field_choices)
                    default_obj.save()

            if field_choices is not None:
                field_choices = [{'id': str(choice[0]), 'legend': str(
                    choice[1])} for choice in field_choices]
                has_default = TemplateMainFieldChoices.objects.filter(
                    field=main, choices=field_choices).exists()
                if not has_default:
                    default_obj = TemplateMainFieldChoices(
                        field_id=main.id, choices=field_choices)
                    default_obj.save()

        for fund in summary_main_fields:
            defaults = fund.copy()
            defaults['template'] = new_template
            TemplateMainSummaryField.objects.get_or_create(
                defaults=defaults, **defaults)
        new_template_rate, created = TemplateRate.objects.get_or_create(
            template=new_template, **template)
        new_template_rate.has_commit = has_commit
        new_template_rate.save()
        if created is False:
            TemplateFieldDefault.objects.filter(
                field__rate=new_template_rate).delete()
            TemplateField.objects.filter(rate=new_template_rate).delete()
            TemplateSummaryField.objects.filter(
                rate=new_template_rate).delete()

            main, created = TemplateField.objects.get_or_create(
                defaults=defaults, **defaults)

            main, created = TemplateField.objects.get_or_create(
                defaults=defaults, **defaults)

            if field_default is not None:
                has_default = TemplateFieldDefault.objects.filter(
                    field=main, label=field_default).exists()
                if not has_default:
                    default_obj = TemplateFieldDefault(field_id=main.id, label=str(field_default),
                                                       value=json.dumps({'data': field_default}))
                    default_obj.save()

            if field_choices is not None:
                field_choices = [{'id': str(choice[0]), 'legend': str(
                    choice[1])} for choice in field_choices]
                has_default = TemplateFieldChoices.objects.filter(
                    field=main, choices=field_choices).exists()
                if not has_default:
                    default_obj = TemplateFieldChoices(
                        field_id=main.id, choices=field_choices)
                    default_obj.save()

        for field in fields_default_all:
            defaults = field.copy()
            defaults['rate'] = new_template_rate
            TemplateField.objects.get_or_create(defaults=defaults, **defaults)
        for field in summary_fields:
            defaults = field.copy()
            defaults['rate'] = new_template_rate
            TemplateSummaryField.objects.get_or_create(
                defaults=defaults, **defaults)


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
    FundDocument.objects.filter(
        template_id__in=old_id).update(template_id=new_id)
    FundIRRF.objects.filter(template_id__in=old_id).update(template_id=new_id)


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        TemplateFundFront().create_templates()
        # correct_verbas()
        # delete_verbas()
