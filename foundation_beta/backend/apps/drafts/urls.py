from django.urls import path

from apps.drafts import views


urlpatterns = [
    path("drafts", views.DraftListView.as_view(), name="draft-list"),
    path("drafts/<uuid:draft_id>", views.DraftDetailView.as_view(), name="draft-detail"),
    path("drafts/<uuid:draft_id>/approve", views.DraftApproveView.as_view(), name="draft-approve"),
    path("drafts/<uuid:draft_id>/edit", views.DraftEditView.as_view(), name="draft-edit"),
    path("drafts/<uuid:draft_id>/reject", views.DraftRejectView.as_view(), name="draft-reject"),
    path("drafts/<uuid:draft_id>/cancel", views.DraftCancelView.as_view(), name="draft-cancel"),
]
