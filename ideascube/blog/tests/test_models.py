from django.db import IntegrityError
import pytest

from ideascube.blog.models import Content

from .factories import ContentFactory

pytestmark = pytest.mark.django_db


def test_get_author_display_should_return_author_text(published):
    text = 'An author'
    published.author_text = text
    assert published.get_author_display() == text


def test_get_author_display_should_return_author_if_no_author_text(user):
    content = ContentFactory(author=user)
    content.author_text = ''
    assert content.get_author_display() == str(user)


def test_cannot_delete_user_if_author_of_blog_content(user):
    content = ContentFactory(author=user)
    with pytest.raises(IntegrityError):
        user.delete()
    assert Content.objects.get(pk=content.pk)
