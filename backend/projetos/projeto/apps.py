from django.apps import AppConfig


class ProjetoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projeto'

    def ready(self):
        # Not Importing.. dont know why..
        import projetos.projeto.signals
        #print("imported!!")