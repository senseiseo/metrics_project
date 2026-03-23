import os
from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.conf import settings


@shared_task(name="apps.metrics.tasks.generate_fake_report")
def generate_fake_report() -> str:
    from apps.metrics.models import Metric, MetricRecord

    metrics_count: int = Metric.objects.count()
    records_count: int = MetricRecord.objects.count()
    now: str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    report_content = (
        f"=== Metrics Fake Report ===\n"
        f"Generated at : {now}\n"
        f"---------------------------\n"
        f"Total Metrics : {metrics_count}\n"
        f"Total Records : {records_count}\n"
        f"===========================\n"
    )

    reports_dir: Path = getattr(settings, "REPORTS_DIR", Path("/app/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path: Path = reports_dir / "report.txt"
    report_path.write_text(report_content, encoding="utf-8")

    return f"Report updated: metrics={metrics_count}, records={records_count}"
