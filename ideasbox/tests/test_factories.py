import pytest

from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_it_should_create_a_default_user_from_factory():
    user = UserFactory()
    assert user.pk is not None
    assert unicode(user)


def test_it_should_override_fields_passed_to_factory():
    user = UserFactory()
    assert user.short_name == "Sankara"
    another = UserFactory(short_name="Che")
    assert another.short_name == "Che"
