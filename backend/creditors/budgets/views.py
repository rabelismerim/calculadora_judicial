
from rest_framework import generics

from .serializers import BudgetsSerializer
from creditors.budgets.models import Budgets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response


class BudgetsCreate(generics.CreateAPIView):

    queryset = Budgets.objects.all().order_by('-id')
    serializer_class = BudgetsSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        budget_pk = self.kwargs.get("budget_pk")
        budget = get_object_or_404(budget, pk=budget_pk)

        serializer.save(budget=budget)
