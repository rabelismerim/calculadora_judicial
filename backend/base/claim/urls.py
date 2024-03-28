from django.urls import path

from base.claim.views import ClaimCreditorApi, ClaimLawyerApi, ClaimCreditorUpdateApi, ClaimLawyerDeleteApi

urlpatterns = [
    # path('', CoinsApi.as_view(), name="coins-list-create"),
    # TODO Marcelo: Criar um get que traga os pleitos recebendo o id do credor
    path('claim-creditor/', ClaimCreditorApi.as_view(), name="claim-creditor-create"),
    path('claim-creditor/<uuid:id>/', ClaimCreditorUpdateApi.as_view(), name="claim-creditor-update"),
    path('claim-lawyer/', ClaimLawyerApi.as_view(), name="claim-lawyer-create-update"),
    path('claim-lawyer/<uuid:id>/', ClaimLawyerDeleteApi.as_view(), name="claim-lawyer-delete"),
]
