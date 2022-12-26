from django.db import models
from django.db.models import Count, Min, Sum, Avg

from core.dttuser.models import User

#from projetos.models import Profissional

class Projeto(models.Model):
    '''Class responsible for the grand project/engagement'''

    eng_number = models.PositiveIntegerField(null=True, blank=True)
    client = models.CharField(max_length=100)
    #users = models.ManyToManyField(Profissional, related_name="projetos") # This is here only for future use (MAYBE)
    user = models.ManyToManyField(User, related_name="projetos") # USE THIS ONE
    image = models.ImageField(null=True, blank=True)
    project_start = models.DateField(null=True, blank=True)
    project_end = models.DateField(null=True, blank=True)
    status = models.CharField(default="Em andamento", max_length=100) # Em andamento | Concluído | Em análise | Cancelado
    #porcentage = models.PositiveIntegerField(default=0) # int 0 to 100
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client} | {str(self.eng_number)}"
    
    @property
    def count_assets(self):
        counter = 0
        for unidade in self.unidades.all():
            for ativo in unidade.ativos_fixos.all():
                counter +=1
        return counter

    @property
    def porcentage_complete(self):

        qt_assets = self.count_assets

        completed_assets = 0
        for unidade in self.unidades.all():
            #print(unidade)
            for ativo in unidade.ativos_fixos.all():
                if ativo.status == True:
                    completed_assets +=1
        if qt_assets != 0:
            return completed_assets/qt_assets * 100
        else:
            return qt_assets
