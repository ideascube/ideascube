from datetime import datetime, timedelta, timezone

import pytest

from ..models import Content
from .factories import ContentFactory


@pytest.fixture()
def published():
    return ContentFactory(status=Content.PUBLISHED)


@pytest.fixture()
def published_in_the_future():
    publication_date = datetime.now(timezone.utc) + timedelta(days=10)
    return ContentFactory(status=Content.PUBLISHED,
                          published_at=publication_date)


@pytest.fixture()
def draft():
    return ContentFactory(status=Content.DRAFT)


@pytest.fixture()
def deleted():
    return ContentFactory(status=Content.DELETED)
