import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.metrics.models import MetricRecord
from apps.metrics.tests.factories import (
    MetricFactory,
    MetricRecordFactory,
    TagFactory,
    UserFactory,
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def auth_client(api_client: APIClient, user) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def metric(user):
    return MetricFactory(owner=user)


@pytest.fixture
def other_metric(other_user):
    return MetricFactory(owner=other_user)


def records_url(metric_id: int) -> str:
    return reverse("metric-record-list-create", kwargs={"metric_id": metric_id})


@pytest.mark.django_db
class TestCreateMetricRecord:
    """Tests for POST /api/metrics/{metric_id}/records/"""

    def test_create_record_success(self, auth_client: APIClient, metric) -> None:
        """A valid request creates a record and returns 201."""
        payload = {"value": "42.5", "note": "Test note"}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert MetricRecord.objects.filter(metric=metric).count() == 1
        data = response.json()
        assert data["value"] == "42.5000"
        assert data["note"] == "Test note"

    def test_create_record_with_tags(self, auth_client: APIClient, metric) -> None:
        """Record can be created with tag IDs."""
        tag1 = TagFactory()
        tag2 = TagFactory()
        payload = {"value": "10.0", "tag_ids": [tag1.id, tag2.id]}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        record = MetricRecord.objects.get(pk=response.json()["id"])
        tag_ids = set(record.tags.values_list("id", flat=True))
        assert tag_ids == {tag1.id, tag2.id}

    def test_create_record_without_tags(self, auth_client: APIClient, metric) -> None:
        """Tags field is optional - record can be created without tags."""
        payload = {"value": "0.0"}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        record = MetricRecord.objects.get(pk=response.json()["id"])
        assert record.tags.count() == 0

    def test_create_record_requires_auth(self, api_client: APIClient, metric) -> None:
        """Unauthenticated request returns 401."""
        payload = {"value": "99.9"}
        response = api_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_record_other_users_metric_returns_404(
        self, auth_client: APIClient, other_metric
    ) -> None:
        """Cannot add a record to another user's metric — returns 404."""
        payload = {"value": "5.0"}
        response = auth_client.post(records_url(other_metric.id), payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_record_nonexistent_metric_returns_404(
        self, auth_client: APIClient
    ) -> None:
        """Non-existent metric_id returns 404."""
        payload = {"value": "5.0"}
        response = auth_client.post(records_url(99999), payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_record_missing_value_returns_400(
        self, auth_client: APIClient, metric
    ) -> None:
        """Value field is required — missing it returns 400."""
        payload = {"note": "no value here"}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in response.json()

    def test_create_record_invalid_value_returns_400(
        self, auth_client: APIClient, metric
    ) -> None:
        """Non-numeric value returns 400."""
        payload = {"value": "not-a-number"}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_record_invalid_tag_id_returns_400(
        self, auth_client: APIClient, metric
    ) -> None:
        """Non-existent tag ID returns 400."""
        payload = {"value": "1.0", "tag_ids": [99999]}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_record_invalidates_cache(
        self, auth_client: APIClient, metric
    ) -> None:
        """After creation the cache for that metric's records is invalidated."""
        with patch("apps.metrics.views.invalidate_records_cache") as mock_invalidate:
            payload = {"value": "7.77"}
            response = auth_client.post(records_url(metric.id), payload)

            assert response.status_code == status.HTTP_201_CREATED
            mock_invalidate.assert_called_once_with(metric.id)

    def test_create_record_response_structure(
        self, auth_client: APIClient, metric
    ) -> None:
        """Response body contains all expected fields."""
        tag = TagFactory()
        payload = {"value": "100.0", "tag_ids": [tag.id], "note": "check fields"}
        response = auth_client.post(records_url(metric.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        for field in ["id", "metric_id", "value", "recorded_at", "tags", "note", "created_at"]:
            assert field in data, f"Missing field: {field}"
        assert data["metric_id"] == metric.id
        assert len(data["tags"]) == 1
        assert data["tags"][0]["id"] == tag.id

    def test_multiple_records_for_same_metric(
        self, auth_client: APIClient, metric
    ) -> None:
        """Multiple records can be created for the same metric."""
        for i in range(3):
            response = auth_client.post(records_url(metric.id), {"value": str(i)})
            assert response.status_code == status.HTTP_201_CREATED

        assert MetricRecord.objects.filter(metric=metric).count() == 3
