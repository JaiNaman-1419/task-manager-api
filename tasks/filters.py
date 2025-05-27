import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):
    completed = django_filters.BooleanFilter()
    title = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ["completed", "title", "created_at"]
