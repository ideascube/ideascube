from django.conf import settings

import factory
from factory.fuzzy import FuzzyText

from ..models import Book, BookSpecimen


class BookFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Test book {0}".format(n))
    description = "This is a test description"
    section = 'digital'
    lang = settings.LANGUAGE_CODE
    cover = factory.django.ImageField()

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if extracted:
            self.tags.add(*extracted)

    class Meta:
        model = Book


class BookSpecimenFactory(factory.django.DjangoModelFactory):

    barcode = FuzzyText(length=6)
    item = factory.SubFactory(BookFactory)

    class Meta:
        model = BookSpecimen


class DigitalBookSpecimenFactory(BookSpecimenFactory):
    barcode = None
    file = factory.django.FileField(filename='book.epub')
