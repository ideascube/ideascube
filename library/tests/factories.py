from django.conf import settings

import factory
from factory.fuzzy import FuzzyText

from ..models import Book, BookSpecimen


class BookFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Test book {0}".format(n))
    summary = "This is a test summary"
    section = 1
    lang = settings.LANGUAGE_CODE

    class Meta:
        model = Book


class BookSpecimenFactory(factory.django.DjangoModelFactory):

    serial = FuzzyText(length=6)
    book = factory.SubFactory(BookFactory)

    class Meta:
        model = BookSpecimen
