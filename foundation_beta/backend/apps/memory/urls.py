from django.urls import path

from apps.memory import views


urlpatterns = [
    path(
        "memory/agent/<str:agent_id>/context",
        views.MemoryContextView.as_view(),
        name="memory-agent-context",
    ),
    path(
        "memory/proposed",
        views.MemoryProposedListView.as_view(),
        name="memory-proposed-list",
    ),
    path(
        "memory/proposed/<uuid:memory_id>/approve",
        views.MemoryApproveView.as_view(),
        name="memory-proposed-approve",
    ),
    path(
        "memory/proposed/<uuid:memory_id>/reject",
        views.MemoryRejectView.as_view(),
        name="memory-proposed-reject",
    ),
    path(
        "memory/<uuid:memory_id>/deprecate",
        views.MemoryDeprecateView.as_view(),
        name="memory-deprecate",
    ),
]
