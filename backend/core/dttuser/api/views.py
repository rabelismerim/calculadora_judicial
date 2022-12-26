from rest_framework import generics #importing concrete views for endpoints
from .serializers import UserSerializer
from rest_framework.permissions import DjangoModelPermissions
from core.dttuser.models import User
from rest_framework import filters

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]
    queryset = User.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username','email','first_name','last_name']
