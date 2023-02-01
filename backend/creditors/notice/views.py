
from rest_framework import generics

from .serializers import NoticeSerializer
from creditors.notice.models import Notice
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class NoticeCreate(generics.CreateAPIView):

    queryset = Notice.objects.all().order_by('-id')
    serializer_class = NoticeSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        notice_pk = self.kwargs.get("notice_pk")
        notice = get_object_or_404(notice, pk=notice_pk)

        serializer.save(notice=notice)

class addNotice(APIView):
    def post(self, request):
        notice_pk = request.data['notice_pk']
        notice = get_object_or_404(notice, pk=notice_pk)
            
        return Response({'result': 'ok'})



