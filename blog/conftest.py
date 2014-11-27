import pytest

from .models import Content
from .tests.factories import ContentFactory


@pytest.fixture()
def published():
    return ContentFactory(status=Content.PUBLISHED)


@pytest.fixture()
def draft():
    return ContentFactory(status=Content.DRAFT)


@pytest.fixture()
def deleted():
    return ContentFactory(status=Content.DELETED)
