import pytest

from ..models import Document
from .factories import DocumentFactory


@pytest.fixture()
def image():
    return DocumentFactory(type=Document.IMAGE)


@pytest.fixture()
def video():
    return DocumentFactory(type=Document.VIDEO)


@pytest.fixture()
def pdf():
    return DocumentFactory(type=Document.PDF)


@pytest.fixture()
def audio():
    return DocumentFactory(type=Document.AUDIO)


@pytest.fixture()
def text():
    return DocumentFactory(type=Document.TEXT)


@pytest.fixture()
def other():
    return DocumentFactory(type=Document.OTHER)
