from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=64, unique=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Metric(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    unit = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Единица измерения",
        help_text="Например: °C, %, шт, руб",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Метрика"
        verbose_name_plural = "Метрики"
        ordering = ["-created_at"]
        unique_together = [["owner", "name"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner.username})"


class MetricRecord(models.Model):
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Метрика",
    )
    value = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Значение",
    )
    recorded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время записи",
        db_index=True,
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="records",
        verbose_name="Тэги",
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Примечание",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "Запись метрики"
        verbose_name_plural = "Записи метрик"
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"{self.metric.name}: {self.value} @ {self.recorded_at:%Y-%m-%d %H:%M}"
