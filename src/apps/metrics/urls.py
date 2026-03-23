from django.urls import path

from .views import (
    MetricListCreateView,
    MetricRecordDetailView,
    MetricRecordListCreateView,
    TagListView,
)

urlpatterns = [
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("metrics/", MetricListCreateView.as_view(), name="metric-list-create"),
    path(
        "metrics/<int:metric_id>/records/",
        MetricRecordListCreateView.as_view(),
        name="metric-record-list-create",
    ),
    path(
        "metrics/<int:metric_id>/records/<int:pk>/",
        MetricRecordDetailView.as_view(),
        name="metric-record-detail",
    ),
]
