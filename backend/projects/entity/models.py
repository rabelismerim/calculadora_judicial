from django.db import models
from core.abstract.models import AbstractModel


class Entity(AbstractModel):
    '''Class responsible for detils to recuperanda or credores'''

    name = models.CharField(max_length=150)
    legal_number = models.CharField(max_length=14)
    # TODO: Criar validador de cpf|cnpj
