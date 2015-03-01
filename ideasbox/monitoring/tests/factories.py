import factory

from ideasbox.tests.factories import UserFactory

from ..models import Entry


class EntryFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    module = 'cinema'

    class Meta:
        model = Entry
