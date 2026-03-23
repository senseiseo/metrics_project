from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from .cache import cache_records, get_cached_records, invalidate_records_cache
from .models import Metric, MetricRecord, Tag
from .serializers import (
    MetricRecordDetailSerializer,
    MetricRecordSerializer,
    MetricSerializer,
    TagSerializer,
)


class TagListView(generics.ListAPIView):
    """
    GET /api/tags/
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class MetricListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/metrics/
    POST /api/metrics/
    """

    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Metric]:
        return Metric.objects.filter(owner=self.request.user)


class MetricRecordListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/metrics/{metric_id}/records/
    POST /api/metrics/{metric_id}/records/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> type:
        return MetricRecordSerializer

    def _get_metric(self) -> Metric:
        metric_id: int = self.kwargs["metric_id"]
        return generics.get_object_or_404(
            Metric, pk=metric_id, owner=self.request.user
        )

    def get_queryset(self) -> QuerySet[MetricRecord]:
        metric = self._get_metric()
        return (
            MetricRecord.objects.filter(metric=metric)
            .prefetch_related("tags")
            .order_by("-recorded_at")
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        metric_id: int = self.kwargs["metric_id"]
        self._get_metric()

        cached = get_cached_records(metric_id)
        if cached is not None:
            return Response(cached)

        queryset = self.get_queryset()
        serializer = MetricRecordSerializer(queryset, many=True)
        data = serializer.data
        cache_records(metric_id, data)
        return Response(data)

    def perform_create(self, serializer: MetricRecordSerializer) -> None:  # type: ignore[override]
        metric = self._get_metric()
        record: MetricRecord = serializer.save(metric=metric)
        invalidate_records_cache(record.metric_id)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = MetricRecordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MetricRecordDetailView(generics.RetrieveAPIView):
    """
    GET /api/metrics/{metric_id}/records/{pk}/
    """

    serializer_class = MetricRecordDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> MetricRecord:
        metric_id: int = self.kwargs["metric_id"]
        record_pk: int = self.kwargs["pk"]
        return generics.get_object_or_404(
            MetricRecord.objects.prefetch_related("tags").select_related("metric"),
            pk=record_pk,
            metric__id=metric_id,
            metric__owner=self.request.user,
        )
