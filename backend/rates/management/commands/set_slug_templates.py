from django.core.management.base import BaseCommand
from xlsxwriter.contenttypes import defaults

from rates.models import TemplateRate, TemplateSlugChoices, TemplateSummaryField, TemplateMainSummaryField, Template


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        for template in TemplateRate.objects.all():
            print(template.end_point)

            if str(template.end_point).endswith('irrf/labor/'):
                template.slug = TemplateSlugChoices.IRRF
            elif str(template.end_point).endswith('labor/integrations/'):
                template.slug = TemplateSlugChoices.FUNDS_INTEGRATION
            elif str(template.end_point).endswith('documents/detail/'):
                template.slug = TemplateSlugChoices.DOCUMENT
            elif str(template.end_point).endswith('labor/'):
                template.slug = TemplateSlugChoices.FUNDS
            else:
                print('template nao mapeado')
            template.save()

        TemplateSummaryField.objects.filter(key='total_historical', order=5).update(order=6)

        summary_main_fields_docs = [
            {'label': 'Total', 'key': '', 'type': 'F', 'order': 0, 'is_editable': False,
             'required': False},
            {'label': '', 'key': 'value', 'type': 'F', 'order': 6, 'is_editable': False,
             'required': False},
            {'label': '', 'key': 'corrected_value', 'type': 'F', 'order': 10, 'is_editable': False,
             'required': False},
            {'label': '', 'key': 'fine', 'type': 'F', 'order': 11, 'is_editable': False,
             'required': False},
            {'label': '', 'key': 'interest', 'type': 'F', 'order': 12, 'is_editable': False,
             'required': False},
            {'label': '', 'key': 'amount_due', 'type': 'F', 'order': 13, 'is_editable': False,
             'required': False}
        ]
        summary = TemplateMainSummaryField.objects.filter(template__name__in=["Acordos", 'Documentos'])
        templates = list(summary.values_list('template_id', flat=True))
        summary.delete()

        for summ in summary_main_fields_docs:
            for template in templates:
                summ['template_id'] = template
                TemplateMainSummaryField.objects.get_or_create(defaults=summ, **summ)
