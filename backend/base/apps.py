from django.apps import AppConfig
from django.db import ProgrammingError, OperationalError

from utils import _


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        from base.models import NatureChoice, NATURES
        natures = NATURES
        try:
            list_natures = NatureChoice.objects.all()
            natures_bulk = []
            for nature_en, nature_pt in natures:
                if not list_natures.filter(description=nature_en).exists():
                    new_nature = NatureChoice(description=nature_en, description_en=nature_en, description_pt_br=nature_pt)
                    natures_bulk.append(new_nature)
            NatureChoice.objects.bulk_create(natures_bulk)

        except (ProgrammingError, OperationalError):
            pass
        return super().ready()
