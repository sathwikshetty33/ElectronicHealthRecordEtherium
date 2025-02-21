from django.urls import path
from .views import ContractOwnerView

urlpatterns = [
    path("", ContractOwnerView.as_view(), name="get-owner"),
]
