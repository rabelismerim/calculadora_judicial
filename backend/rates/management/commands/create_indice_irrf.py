from django.core.management.base import BaseCommand
from rates.models import IndiceIRRF, get_aliquot_by_tax


def create_irrf_values():
    """Create Index IRRF"""
    irrf_values = [
        {'id': '4a85c439-06f5-4c40-9e31-1618bccb1a3f', 'start': 0, 'end': 1903.98, 'aliquot': 0, 'deduction': 0},
        {'id': 'a06d3d0f-6374-4a13-ab39-01cd3e42b45a', 'start': 1903.99, 'end': 2826.65, 'aliquot': 7.5,
         'deduction': 142.80},
        {'id': '8a2eba28-c1c4-4d08-9814-6c80e798df58', 'start': 2826.66, 'end': 3751.05, 'aliquot': 15,
         'deduction': 354.80},
        {'id': '9378924e-2caf-4234-be2f-832472e3c51a', 'start': 3751.06, 'end': 4664.68, 'aliquot': 22.5,
         'deduction': 636.13},
        {'id': '951aa6ff-49ea-48da-8781-70b2d7cb9045', 'start': 4664.69, 'end': float('inf'), 'aliquot': 27.5,
         'deduction': 869.36},
    ]

    for irrf in irrf_values:
        irrf_obj = IndiceIRRF.objects.filter(id=irrf['id']).first()
        if not irrf_obj:
            irrf_obj = IndiceIRRF(reference_year='2020', **irrf)
            irrf_obj.save()

    assert get_aliquot_by_tax(0).deduction == 0
    assert get_aliquot_by_tax(5).deduction == 0
    assert get_aliquot_by_tax(1903.98).deduction == 0
    assert get_aliquot_by_tax(1903.99).deduction == 142.80
    assert get_aliquot_by_tax(2826.65).deduction == 142.80
    assert get_aliquot_by_tax(2826.66).deduction == 354.80
    assert get_aliquot_by_tax(3751.05).deduction == 354.80
    assert get_aliquot_by_tax(3751.06).deduction == 636.13
    assert get_aliquot_by_tax(4664.68).deduction == 636.13
    assert get_aliquot_by_tax(4664.69).deduction == 869.36
    assert get_aliquot_by_tax(5000.00).deduction == 869.36
    print('\033[92m Successful created aliquots')


class Command(BaseCommand):
    help = 'Create IRRF values'

    def handle(self, *args, **options):
        create_irrf_values()
