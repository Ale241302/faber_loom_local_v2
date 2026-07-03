from django.urls import path

from apps.learning import views

urlpatterns = [
    path("learning/ledger", views.LedgerListView.as_view(), name="learning-ledger-list"),
    path("learning/candidates", views.CandidateListView.as_view(), name="learning-candidates-list"),
    path("learning/candidates/<uuid:gold_id>/promote", views.CandidatePromoteView.as_view(), name="learning-candidate-promote"),
    path("learning/candidates/<uuid:gold_id>/discard", views.CandidateDiscardView.as_view(), name="learning-candidate-discard"),
    path("learning/gold/<uuid:gold_id>/second-approve", views.GoldSecondApproveView.as_view(), name="learning-gold-second-approve"),
    path("learning/gold/<uuid:gold_id>/deprecate", views.GoldDeprecateView.as_view(), name="learning-gold-deprecate"),
    path("learning/thermometer", views.ThermometerView.as_view(), name="learning-thermometer"),
]
