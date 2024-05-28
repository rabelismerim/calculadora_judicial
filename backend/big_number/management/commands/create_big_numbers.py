import json
import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import F

from big_number.models import BigNumber, BigNumberMethod, BigNumberMethodFields


class Command(BaseCommand):
    help = 'Create data.'

    def handle(self, *args, **options):
        # self.save_big_numbers()
        self.read_big_numbers()

    def save_big_numbers(self):

        big_numbers = BigNumber.objects.all().values('id', 'content_object_id', 'path',
                                                     label=F('content_object__app_label'),
                                                     model=F('content_object__model'))
        big_numbers_method = BigNumberMethod.objects.all().values('id', 'big_number_id', 'method', 'name', 'field_type')
        big_numbers_method_fields = BigNumberMethodFields.objects.all().values('id', 'big_number_method_id', 'field',
                                                                               'field_type')
        logging.info(big_numbers)
        logging.info(big_numbers_method)
        logging.info(big_numbers_method_fields)

        with open('big_numbers.json', 'w') as f:
            f.write(json.dumps(list(big_numbers), default=str))

        with open('big_numbers_method.json', 'w') as f:
            f.write(json.dumps(list(big_numbers_method), default=str))

        with open('big_numbers_method_fields.json', 'w') as f:
            f.write(json.dumps(list(big_numbers_method_fields), default=str))

        self.stdout.write(self.style.SUCCESS('Big numbers salvos em json'))

    def read_big_numbers(self):
        with open('big_numbers.json', 'r') as f:
            big_numbers = json.loads(f.read())

        big_numbers_bulk = []
        all_big_numbers = BigNumber.objects.all()
        for big in big_numbers:
            content_object = ContentType.objects.filter(app_label=big['label'], model=big['model']).first()
            obj = {
                'id': big['id'], 'content_object': content_object,
                'path': big['path']
            }
            big_obj = all_big_numbers.filter(**obj).exists()
            if not big_obj:
                big_numbers_bulk.append(BigNumber(**obj))

        BigNumber.objects.bulk_create(big_numbers_bulk)

        with open('big_numbers_method.json', 'r') as f:
            big_numbers_method = json.loads(f.read())

        big_numbers_method_bulk = []
        all_big_numbers_method = BigNumberMethod.objects.all()
        for big in big_numbers_method:
            obj = {
                'id': big['id'], 'big_number_id': big['big_number_id'],
                'method': big['method'],
                'name': big['name'],
                'field_type': big['field_type']
            }
            big_obj = all_big_numbers_method.filter(**obj).exists()

            if not big_obj:
                big_numbers_method_bulk.append(BigNumberMethod(**obj))

        BigNumberMethod.objects.bulk_create(big_numbers_method_bulk)
        with open('big_numbers_method_fields.json', 'r') as f:
            big_numbers_method_fields = json.loads(f.read())

        big_numbers_method_fields_bulk = []
        all_big_numbers_method_fields = BigNumberMethodFields.objects.all()
        for big in big_numbers_method_fields:
            obj = {
                'id': big['id'],
                'big_number_method_id': big['big_number_method_id'],
                'field': big['field'], 'field_type': big['field_type']
            }
            big_obj = all_big_numbers_method_fields.filter(**obj).exists()

            if not big_obj:
                big_numbers_method_fields_bulk.append(BigNumberMethodFields(**obj))
        BigNumberMethodFields.objects.bulk_create(big_numbers_method_fields_bulk)

        self.stdout.write(self.style.SUCCESS('Big numbers criado nas models'))
