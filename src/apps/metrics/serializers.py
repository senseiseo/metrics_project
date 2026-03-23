from typing import Any

from rest_framework import serializers

from .models import Metric, MetricRecord, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class MetricSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Metric
        fields = ["id", "name", "description", "unit", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        user = self.context["request"].user
        qs = Metric.objects.filter(owner=user, name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "У вас уже есть метрика с таким названием."
            )
        return value


class MetricRecordSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        required=False,
        source="tags",
    )
    metric_id = serializers.IntegerField(source="metric.id", read_only=True)

    class Meta:
        model = MetricRecord
        fields = [
            "id",
            "metric_id",
            "value",
            "recorded_at",
            "tags",
            "tag_ids",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "metric_id", "created_at"]

    def create(self, validated_data: dict[str, Any]) -> MetricRecord:
        tags: list[Tag] = validated_data.pop("tags", [])
        record: MetricRecord = MetricRecord.objects.create(**validated_data)
        if tags:
            record.tags.set(tags)
        return record


class MetricRecordDetailSerializer(MetricRecordSerializer):
    metric = MetricSerializer(read_only=True)

    class Meta(MetricRecordSerializer.Meta):
        fields = MetricRecordSerializer.Meta.fields + ["metric"]
