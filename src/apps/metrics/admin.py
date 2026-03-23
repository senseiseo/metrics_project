from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Metric, MetricRecord, Tag

admin.site.site_header = "Metrics Admin"
admin.site.site_title = "Metrics Admin"
admin.site.index_title = "Управление метриками"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "created_at"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


class MetricRecordInline(admin.TabularInline):
    model = MetricRecord
    extra = 0
    fields = ["value", "recorded_at", "tags", "note"]
    readonly_fields = ["created_at"]
    show_change_link = True


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "unit", "owner", "records_count", "created_at"]
    list_display_links = ["name"]
    list_filter = ["owner"]
    search_fields = ["name", "owner__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [MetricRecordInline]
    ordering = ["-created_at"]

    @admin.display(description="Записей")
    def records_count(self, obj: Metric) -> int:
        return obj.records.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Metric]:
        return super().get_queryset(request).select_related("owner")


@admin.register(MetricRecord)
class MetricRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "metric", "value", "recorded_at", "tag_list", "note"]
    list_display_links = ["metric"]
    list_filter = ["metric__owner", "tags"]
    search_fields = ["metric__name", "note"]
    filter_horizontal = ["tags"]
    readonly_fields = ["created_at"]
    ordering = ["-recorded_at"]

    @admin.display(description="Тэги")
    def tag_list(self, obj: MetricRecord) -> str:
        return ", ".join(tag.name for tag in obj.tags.all()) or "—"

    def get_queryset(self, request: HttpRequest) -> QuerySet[MetricRecord]:
        return (
            super()
            .get_queryset(request)
            .select_related("metric", "metric__owner")
            .prefetch_related("tags")
        )
