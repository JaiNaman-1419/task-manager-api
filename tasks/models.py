from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
