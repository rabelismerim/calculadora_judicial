from django.http import Http404
from django.urls import include, path

from projects.views import ProjectApi, ProjectDetailApi


class VersionedPath:
    def __init__(self, path, version, app_name, namespace, view_class):
        self.path = path
        self.version = version
        self.app_name = app_name
        self.namespace = namespace
        self.view_class = view_class


def versioned_view(view_class, allowed_versions=None):
    """
    Retorna uma view que verifica se a versão solicitada é permitida e atualiza a rota de acordo.
    """
    allowed_versions = allowed_versions or []

    class VersionedView(view_class):
        def dispatch(self, request, *args, **kwargs):
            version = kwargs.get('version')

            # Verifica se a versão solicitada é permitida. Se não for, retorna um erro 404
            if version not in allowed_versions:
                return Http404()

            # Cria uma cópia dos argumentos da URL e atualiza a versão, se necessário
            new_kwargs = kwargs.copy()
            if version != request.version:
                new_kwargs['version'] = request.version

            return super().dispatch(request, *args, **new_kwargs)

    return VersionedView.as_view()


def versioned_patterns(*args):
    """
    Retorna uma lista de urlpatterns com as rotas versionadas especificadas.
    """
    patterns = []
    for arg in args:

        if isinstance(arg, VersionedPath):
            # Adiciona a view versionada à lista de views permitidas para essa versão
            view = versioned_view(arg.view_class.as_view(), allowed_versions=[arg.version])
            # Adiciona a rota atualizada à lista de urlpatterns
            # patterns.append(path(arg.path, arg.view_class, name=arg.view_class.__name__.lower()))
            patterns.append(path(arg.path, view, name=arg.view_class.__name__.lower()))
        else:
            patterns.append(arg)
    return patterns


urlpatterns = [
    # *versioned_patterns(
    #     VersionedPath('<uuid:id>/', 'v1', ProjectDetailApi),
    #     VersionedPath('<uuid:id>/', 'v2', ProjectDetailV2Api),
    # ),

    path('', ProjectApi.as_view(), name="projects-list-create"),
    path('<uuid:id>/', ProjectDetailApi.as_view(), name="project-detail-v1"),
    # path('<uuid:id>/', ProjectDetailV2Api.as_view(), name="project-detail-v2"),

    # path('<uuid:id>/', versioned_view(ProjectDetailApi, allowed_versions=['v1']), name="project-detail-v1"),
    # path('<uuid:id>/', versioned_view(ProjectDetailV2Api, allowed_versions=['v2']), name="project-detail-v2"),

    path('judge/', include("projects.judge.urls")),
    path('lawyer/', include("projects.lawyer.urls")),
    path('region/', include("projects.region.urls")),
    path('court/', include("projects.court.urls")),
    path('engagement/', include("projects.engagement.urls")),
    path('project_user/', include("projects.project_user.urls")),
]
