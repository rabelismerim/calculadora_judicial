
from rest_framework import generics

from .serializers import ArchiveSerializer
from creditors.archive.models import Archive
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response

class ArchiveCreate(generics.CreateAPIView):

    queryset = Archive.objects.all().order_by('-id')
    serializer_class = ArchiveSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        archive_pk = self.kwargs.get("archive_pk")
        archive = get_object_or_404(archive, pk=archive_pk)

        serializer.save(archive=archive)

class addArchive(APIView):
    def post(self, request):
        archive_pk = request.data['archive_pk']
        archive = get_object_or_404(archive, pk=archive_pk)
            
        return Response({'result': 'ok'})



