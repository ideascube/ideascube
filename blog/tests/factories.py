import factory
import datetime

from ideasbox.tests.factories import UserFactory

from ..models import Content


class ContentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Test content %03d" % n)
    summary = "This is a test summary"
    text = "This is a test subtitle"
    author = factory.SubFactory(UserFactory)
    published_at = factory.LazyAttribute(lambda o: datetime.datetime.utcnow())

    class Meta:
        model = Content
