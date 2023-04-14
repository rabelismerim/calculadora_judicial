from django.utils.translation import gettext

from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission
from recovering.archive.models import Archive
from recovering.archive_recovering.models import ArchiveRecovering
from recovering.models import Recovering
from recovering.schemas import RecoveringSchema
from utils import _, doc


class RecoveringApi(AbstractViewApi):
    """HTTP methods for recovering"""

    http_method_names = ['post', 'get']
    serializer_class = RecoveringSchema
    model = Recovering
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    tags = [str(_("Recovering"))]

    query_params = [
        {
            "name": "name",
            "field": "entity__name__icontains",
            "in": "query",
            "required": False,
            "description": _("Name"),
            "schema": {"type": "string"}
        },
        {
            "name": "cpf_cnpj",
            "field": "entity__legal_number__icontains",
            "in": "query",
            "required": False,
            "description": _("CPF/CNPJ"),
            "schema": {"type": "string"}
        }
    ]

    docs = {
        'init': _("""The `Recovering` class is responsible for representing the credit recovery of an entity in a 
           specific project/engagement. It has a relationship with the `Project` model and with the `Entity` model. In 
           addition, it has a recovery status, which can be "Under review", "Completed", "In progress" or "Cancelled".
           """),
        'get': _("""Returns a list of recoverings, containing the details of the recovering, the creditors"""),
    }

    @doc("""Create recovering receiving a dict, return recovering detail""")
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        recovering = serializer.validated_data
        entity = recovering.pop('entity')
        new_archive_recovering = recovering.pop('archives', None)
        recovering['entity'] = Entity.objects.create(**entity)
        new_recovering = self.model.objects.create(**recovering)
        if new_archive_recovering:
            for new_ in new_archive_recovering:
                archive = new_.pop('archive')
                new_archive = Archive.objects.create(**archive)
                ArchiveRecovering.objects.create(recovering=new_recovering, archive=new_archive)
        return JsonResponse({'recovering': self.serializer_class(new_recovering, many=False).data},
                            status=status.HTTP_201_CREATED)
