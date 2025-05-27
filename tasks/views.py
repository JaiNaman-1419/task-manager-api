from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .filters import TaskFilter
from .models import Task
from .permissions import IsOwnerOrAdmin
from .serializers import TaskCreateUpdateSerializer, TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET /tasks: Retrieve a list of all tasks
    POST /tasks: Create a new task
    """

    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Task.objects.all()
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """Automatically set the user to the authenticated user when creating a task"""
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /tasks/{id}: Retrieve details of a specific task
    PUT /tasks/{id}: Update details of a specific task
    DELETE /tasks/{id}: Delete a specific task
    """

    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Task.objects.all()
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return TaskCreateUpdateSerializer
        return TaskSerializer


@api_view(["GET"])
def task_stats(request):
    """Get task statistics for the current user"""
    if request.user.role == "admin":
        queryset = Task.objects.all()
    else:
        queryset = Task.objects.filter(user=request.user)

    total_tasks = queryset.count()
    completed_tasks = queryset.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    return Response(
        {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2
            ),
        }
    )
