"""URL configuration for M10 L1 Classifier."""
from __future__ import annotations

from django.urls import path

from apps.classifier import views

urlpatterns = [
    path("classifier/classify", views.ClassifyView.as_view(), name="classifier-classify"),
    path("classifier/pending", views.PendingView.as_view(), name="classifier-pending"),
    path(
        "classifier/feed-items/<uuid:feed_item_id>/confirm",
        views.ConfirmView.as_view(),
        name="classifier-confirm",
    ),
    path(
        "classifier/feed-items/<uuid:feed_item_id>/reclassify",
        views.ReclassifyView.as_view(),
        name="classifier-reclassify",
    ),
    path("classifier/skills", views.SkillListView.as_view(), name="classifier-skills"),
    path(
        "classifier/skills/<uuid:skill_id>/clone",
        views.SkillCloneView.as_view(),
        name="classifier-skill-clone",
    ),
]
