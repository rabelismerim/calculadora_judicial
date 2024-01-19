from django.core.management.base import BaseCommand

from rates.models import TemplateField, TemplateRate, TemplateMainField, TemplateSummaryField, \
    TemplateMainSummaryField, TemplateMainFieldDefault, TemplateFieldDefault


def delete_verbas():
    TemplateMainField.objects.all().delete()
    TemplateField.objects.all().delete()
    TemplateSummaryField.objects.all().delete()
    TemplateFieldDefault.objects.all().delete()
    TemplateMainFieldDefault.objects.all().delete()
    TemplateMainSummaryField.objects.all().delete()
    TemplateRate.objects.all().delete()


class Command(BaseCommand):
    """
    This class creates templates to rates.

    Attributes:
        help (str): Description of the command.
    """
    help = 'Create templates to rates'

    def handle(self, *args, **options):
        delete_verbas()
