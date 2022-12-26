from django.db.models.signals import post_save
from django.dispatch import receiver
from projetos.ativo.models import Ativo_fixo


@receiver(post_save, sender=Ativo_fixo)
def detectar(sender, instance, created, update_fields, **kwargs):
    #print("Houve mudança no banco de Ativos")
    

    