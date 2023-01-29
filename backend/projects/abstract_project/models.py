from django.db import models
from core.abstract.models import AbstractModel


class AbstractDescription(AbstractModel):
    description = models.CharField('Descrição', max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description


class AbstractInfo(AbstractModel):
    name = models.CharField('Descrição', max_length=150)
    legal_number = models.CharField('CPF/CNPJ', max_length=18)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} - {self.legal_number}'