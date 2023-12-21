from django.core.management.base import BaseCommand

from rates.models import TemplateRate, TemplateSlugChoices


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
