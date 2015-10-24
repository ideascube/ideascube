from django.conf import settings

import factory
from factory.fuzzy import FuzzyText

from ..models import Book, BookSpecimen


class BookFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Test book {0}".format(n))
    summary = "This is a test summary"
    section = 1
    lang = settings.LANGUAGE_CODE
    cover = factory.django.ImageField()

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if extracted:
            self.tags.add(*extracted)

    class Meta:
        model = Book


class BookSpecimenFactory(factory.django.DjangoModelFactory):

    serial = FuzzyText(length=6)
    book = factory.SubFactory(BookFactory)

    @factory.post_generation
    def is_digital(obj, create, extracted, **kwargs):
        if extracted:
            obj.file = 'ideastube/library/tests/data/test-digital'
            obj.serial = None

    class Meta:
        model = BookSpecimen
