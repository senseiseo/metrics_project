import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("metrics_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks()

# Celery Beat schedule — runs every 2 minutes
app.conf.beat_schedule = {
    "generate-fake-report-every-2-minutes": {
        "task": "apps.metrics.tasks.generate_fake_report",
        "schedule": 120.0,
    },
}
