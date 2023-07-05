from django.apps import AppConfig
from django.db import ProgrammingError, OperationalError

from utils import _


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        from base.models import NatureChoice
        natures = [
            (_('Extrajudicial enforcement action'), _('Ação de execução de título extrajudicial')),
            (_('Bank contract'), _('Contrato bancário')),
            (_('Miscellaneous contracts'), _('Contratos diversos')),
            (_('Advocative hours'), _('Honorários advocatícios')),
            (_('Invoice'), _('Nota fiscal')),
            (_('Rural producer contract'), _('Contrato de produtor rural')),
            (_('Legal title'), _('Título judicial')),
            (_('Labor'), _('Trabalhista')),
            (_('Labor Union'), _('Trabalhista Sindicato')),
            (_('Promissory note'), _('Nota promissória')),
            (_('AT'), _('N/A')),
        ]
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
