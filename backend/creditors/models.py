from django.db import models
from core.entity.models import Entity
from recovering.models import Recovering
from base.models import AbstractDateCreditor


class Creditor(AbstractDateCreditor):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    recovering = models.ForeignKey(
        Recovering, on_delete=models.PROTECT)
    description = models.CharField('Descrição', max_length=255, null=True)
