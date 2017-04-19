from django.db import IntegrityError
import pytest

from ideascube.blog.models import Content

from .factories import ContentFactory

pytestmark = pytest.mark.django_db


def test_cannot_delete_user_if_author_of_blog_content(user):
    content = ContentFactory(author=user)
    with pytest.raises(IntegrityError):
        user.delete()
    assert Content.objects.get(pk=content.pk)
