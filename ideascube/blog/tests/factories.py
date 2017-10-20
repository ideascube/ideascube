from datetime import datetime, timedelta, timezone

import factory

from ideascube.tests.factories import UserFactory

from ..models import Content


class ContentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Test content %03d" % n)
    summary = "This is a test summary"
    text = "This is a test subtitle"
    lang = 'en'
    author = factory.SubFactory(UserFactory)
    published_at = factory.LazyAttribute(
        lambda o: datetime.now(timezone.utc) - timedelta(hours=1))
    image = factory.django.ImageField()

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if extracted:
            self.tags.add(*extracted)

    class Meta:
        model = Content
