from django.db import models

class Notice(models.Model):
    id_entity = models.ForeignKey("projetos.project", on_delete=models.CASCADE, related_name="Projeto")
    id_class = models.ForeignKey("creditors.classes", on_delete=models.CASCADE, related_name="Classe")
    id_coins = models.ForeignKey("creditors.coins", on_delete=models.CASCADE, related_name="Moeda")
    value = models.FloatField()
    archive_json = models.TextField(blank=True) 

    def __str__(self):
        return f"{self.id} | {str(self.id_client)}"
    