from rest_framework import generics #importing concrete views for endpoints
from .serializers import ProjetoListSerializer, ProjetoDetailSerializer
from projetos.projeto.models import Projeto
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth.models import User



class ProjetoListCreate(generics.ListCreateAPIView):

    # We need to be able to filter the projects, so queryset is defined inside the get_queryset() method
    #queryset = Projeto.objects.all().order_by('-id')

    serializer_class = ProjetoListSerializer
    permission_classes = [DjangoModelPermissions]

    # grabed the super dispatch to access request.user
    def dispatch(self, request, *args, **kwargs):
        self.usuario = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        '''
        filters the resulting queryset based on the params in the url and current user
        '''
        queryset = Projeto.objects.filter(user__username=self.request.user).order_by('-id')
        return queryset
    
    def post(self, request):
        ''' responsible for sending the api request after checking queue and returns sucess'''
        data=request.data
        serializer = ProjetoListSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # REJECTS BAD REQUESTS
        else:
            serializer.validated_data['user'].append(self.request.user) # adds current user to project
            serializer.validated_data['is_active'] = True
            projeto = serializer.save() # SAVES IN DB THE project
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjetoDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ProjetoDetailSerializer
    permission_classes = [DjangoModelPermissions]

    # grabed the super dispatch to access request.user
    def dispatch(self, request, *args, **kwargs):
        self.usuario = request.user
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        '''
        filters the resulting queryset based on the current user
        '''
        queryset = Projeto.objects.filter(user__username=self.request.user).order_by('-id')
        return queryset



