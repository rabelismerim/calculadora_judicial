
from rest_framework import generics

from .serializers import ArchiveRecoveringSerializer
from creditors.archive_recovering.models import ArchiveRecovering
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class ArchiveRecoveringCreate(generics.CreateAPIView):

    queryset = ArchiveRecovering.objects.all().order_by('-id')
    serializer_class = ArchiveRecovering
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        archive_recovering_pk = self.kwargs.get("archive_recovering_pk")
        archive_recovering = get_object_or_404(archive_recovering, pk=archive_recovering_pk)

        serializer.save(archive_recovering=archive_recovering)

class addArchiveRecovering(APIView):
    def post(self, request):
        archive_recovering_pk = request.data['archive_recovering_pk']
        archive_recovering = get_object_or_404(archive_recovering, pk=archive_recovering_pk)
            
        return Response({'result': 'ok'})



