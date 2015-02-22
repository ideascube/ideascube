import pytest

from .factories import ContentFactory

pytestmark = pytest.mark.django_db


def test_it_should_create_a_default_content_from_factory():
    content = ContentFactory()
    assert content.pk is not None
    assert unicode(content)


def test_it_should_override_fields_passed_to_factory():
    content = ContentFactory()
    assert content.title.startswith('Test content')
    another = ContentFactory(title="My custom title")
    assert another.title == "My custom title"


def test_can_create_content_without_image():
    assert ContentFactory(image=None)
