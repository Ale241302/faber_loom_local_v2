"""URL routes for M11 D9 Policy Gate."""
from django.urls import path

from apps.policy import views

urlpatterns = [
    path("policy/dpa", views.DpaStatusView.as_view(), name="policy-dpa-status"),
    path("policy/dpa/sign", views.DpaSignView.as_view(), name="policy-dpa-sign"),
    path("policy/evaluate", views.PolicyEvaluateView.as_view(), name="policy-evaluate"),
    path("policy/blocks", views.PolicyBlocksView.as_view(), name="policy-blocks"),
]
