from django.db import models
from core.entity.models import Entity
from recovering.models import Recovering
from base.models import AbstractDateCreditor


class Creditor(AbstractDateCreditor):
    # TODO: filtrar Entity se já existe nessa recuperanda
    # Entidade(dados credor)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    recovering = models.ForeignKey(
        Recovering, on_delete=models.PROTECT)  # Recuperanda
    # notice = models.ForeignKey(
    #     Notice, on_delete=models.PROTECT, null=True)  # Edital
