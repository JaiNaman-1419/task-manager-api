from django.urls import path

from . import views

urlpatterns = [
    path("tasks/", views.TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("tasks/stats/", views.task_stats, name="task-stats"),
]
