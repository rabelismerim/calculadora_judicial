from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.apps import apps as default_apps
from config.settings import INSTALLED_APPS

all_projects = {
    'content_type': 'project',
    'codename': 'can_view_all_projects',
    'name': 'Can view all Projects'
}
authorize_users = {
    'content_type': 'dttuser',
    'codename': 'can_authorize_users',
    'name': 'Can authorize Users'
}
groups = [
    {'name': 'Gestor Financeiro',
     'models': [
         {'name': 'project',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'base',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'recovering',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'calculation',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'creditors',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'dttuser',
          'actions': ['view', 'add', 'change', 'delete'],
          }
     ],
     'custom_perms': [all_projects, authorize_users]
     },
    {'name': 'Gestor Cálculo',
     'models': [
         {'name': 'project',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'base',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'recovering',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'calculation',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'creditors',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'dttuser',
          'actions': ['view', 'add', 'change', 'delete'],
          }
     ],
     'custom_perms': [all_projects, authorize_users]
     },
    {'name': 'Gestor Jurídico',
     'models': [
         {'name': 'project',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'base',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'recovering',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'calculation',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'creditors',
          'actions': ['view', 'add', 'change', 'delete'],
          },
         {'name': 'dttuser',
          'actions': ['view', 'add', 'change', 'delete'],
          }
     ],
     'custom_perms': [all_projects, authorize_users]
     },
    {'name': 'Consultor Financeiro',
     'models': [
         {'name': 'project',
          'actions': ['view'],
          },
         {'name': 'base',
          'actions': ['view'],
          },
         {'name': 'recovering',
          'actions': ['view'],
          },
         {'name': 'calculation',
          'actions': ['view'],
          },
         {'name': 'creditors',
          'actions': ['view'],
          },
         {'name': 'dttuser',
          'actions': ['view'],
          }
     ],
     'custom_perms': []
     },
    {'name': 'Consultor Cálculo',
     'models': [
         {'name': 'project',
          'actions': ['view'],
          },
         {'name': 'base',
          'actions': ['view'],
          },
         {'name': 'recovering',
          'actions': ['view'],
          },
         {'name': 'calculation',
          'actions': ['view'],
          },
         {'name': 'creditors',
          'actions': ['view'],
          },
         {'name': 'dttuser',
          'actions': ['view'],
          }
     ],
     'custom_perms': []
     },
    {'name': 'Consultor Jurídico',
     'models': [
         {'name': 'project',
          'actions': ['view'],
          },
         {'name': 'base',
          'actions': ['view'],
          },
         {'name': 'recovering',
          'actions': ['view'],
          },
         {'name': 'calculation',
          'actions': ['view'],
          },
         {'name': 'creditors',
          'actions': ['view'],
          },
         {'name': 'dttuser',
          'actions': ['view'],
          }
     ],
     'custom_perms': []
     }
]


class Command(BaseCommand):
    """
    This base command is responsible for creating groups with specific permissions for the Django platform.
    """
    help = 'run create permissions group'

    def print_start(self, msg):
        """
        Print the message msg with the success style on the console.
        """
        self.stdout.write(self.style.SUCCESS(msg))

    def __get_apps(self, app_label):
        """
        Parameters:
        - app_label (string): label of the application.
        Return the list of applications that start with the app_label parameter.
        """
        apps = INSTALLED_APPS.copy()
        apps.append('dttuser.User')
        return [app for app in apps if app.startswith(app_label)]

    def create_groups(self):
        """
        Create the groups with their respective permissions using the Django Group and Permission models,
        based on the parameters of the classes and actions.
        """
        for group in groups:
            group_object, created = Group.objects.get_or_create(name=group['name'])
            perms = []
            for model in group['models']:
                apps = self.__get_apps(model['name'])
                for app in apps:
                    app_name = app.split('.')
                    model_name = app_name[-1] if len(app_name) > 1 else app_name[0]
                    app_models = default_apps.all_models[model_name]

                    for action in model['actions']:
                        for model_ in app_models.values():
                            codename = f"{action}"
                            per = Permission.objects.filter(
                                content_type__model__icontains=model_._meta.model_name,
                                codename__icontains=codename
                            ).values_list('id', flat=True)
                            perms.extend(per)

            for custom_perm in group['custom_perms']:
                content = custom_perm.get('content_type')
                codename = custom_perm.get('codename')
                name = custom_perm.get('name')
                content_type = ContentType.objects.filter(app_label__icontains=content).first()
                permission, created = Permission.objects.get_or_create(content_type=content_type, codename=codename,
                                                                       name=name)
                perms.append(permission.id)
            group_object.permissions.add(*perms)
            group_object.save()
            self.print_start(
                f'Successfully {"created" if created else "altered"} group {group["name"]}\nNumber of permissions: '
                f'{len(perms)}')
        group_object, created = Group.objects.get_or_create(name='Administrador')
        perms = list(
            Permission.objects.exclude(content_type__app_label__in=['authtoken', 'admin', 'auth', 'contenttypes',
                                                                    'sessions', 'sites']).values_list('id', flat=True))

        # Create group Admin
        group_object.permissions.add(*perms)
        group_object.save()
        self.print_start(
            f'Successfully {"created" if created else "altered"} group Administrador\nNumber of permissions: '
            f'{len(perms)}')

    def handle(self, *args, **options):
        self.create_groups()
