import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.metrics.models import Metric, MetricRecord, Tag

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpassword123")


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag_{n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.replace(" ", "-"))


class MetricFactory(DjangoModelFactory):
    class Meta:
        model = Metric

    name = factory.Sequence(lambda n: f"metric_{n}")
    description = "Test metric description"
    unit = "units"
    owner = factory.SubFactory(UserFactory)


class MetricRecordFactory(DjangoModelFactory):
    class Meta:
        model = MetricRecord

    metric = factory.SubFactory(MetricFactory)
    value = factory.Sequence(lambda n: n * 1.5)
    note = "Test note"
