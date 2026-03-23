import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create superuser from environment variables if not exists"

    def handle(self, *args: object, **options: object) -> None:
        username: str = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email: str = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password: str = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' created successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser '{username}' already exists. Skipping.")
            )
