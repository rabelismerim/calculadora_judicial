
from rest_framework import generics

from .serializers import ClassesSerializer
from creditors.classes.models import Classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class ClassesCreate(generics.CreateAPIView):

    queryset = Classes.objects.all().order_by('-id')
    serializer_class = ClassesSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        classes_pk = self.kwargs.get("classes_pk")
        classes = get_object_or_404(classes, pk=classes_pk)

        serializer.save(classes=classes)

class addClasses(APIView):
    def post(self, request):
        classes_pk = request.data['classes_pk']
        classes = get_object_or_404(classes, pk=classes_pk)
            
        return Response({'result': 'ok'})



