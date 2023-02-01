
from rest_framework import generics

from .serializers import CoinsSerializer
from creditors.coins.models import Coins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class CoinsCreate(generics.CreateAPIView):

    queryset = Coins.objects.all().order_by('-id')
    serializer_class = CoinsSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        coins_pk = self.kwargs.get("coins_pk")
        coins = get_object_or_404(coins, pk=coins_pk)

        serializer.save(coins=coins)

class addCoins(APIView):
    def post(self, request):
        coins_pk = request.data['coins_pk']
        coins = get_object_or_404(coins, pk=coins_pk)
            
        return Response({'result': 'ok'})



