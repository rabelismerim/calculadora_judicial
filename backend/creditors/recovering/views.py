
from rest_framework import generics

from .serializers import RecoveringSerializer
from creditors.recovering.models import Recovering
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class RecoveringCreate(generics.CreateAPIView):

    queryset = Recovering.objects.all().order_by('-id')
    serializer_class = RecoveringSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        recovering_pk = self.kwargs.get("recovering_pk")
        recovering = get_object_or_404(recovering, pk=recovering_pk)

        serializer.save(recovering=recovering)

class addRecovering(APIView):
    def post(self, request):
        recovering_pk = request.data['recovering_pk']
        recovering = get_object_or_404(recovering, pk=recovering_pk)
            
        return Response({'result': 'ok'})



