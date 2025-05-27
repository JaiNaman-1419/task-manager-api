from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        user = serializers.StringRelatedField(read_only=True)

        model = Task
        fields = ["id", "title", "description", "completed", "created_at", "updated_at", "user"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "completed"]
