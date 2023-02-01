from django.db import models

class Coins(models.Model):

    description = (
        ("B","BRL"),
        ("E","EUR"),
        ("U","US$"),
        ("C","CAN$")
    )        
    models.CharField(max_length=1, verbose_name='Descrição', choices=description)

    def __str__(self):
        return f"{self.description}"
    