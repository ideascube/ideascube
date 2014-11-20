import factory
from factory.fuzzy import FuzzyText
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    serial = FuzzyText(length=12)
    short_name = "Sankara"
    full_name = "Thomas Sankara"

    class Meta:
        model = get_user_model()
