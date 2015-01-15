import pytest

from ..models import Document
from .factories import DocumentFactory


@pytest.fixture()
def image():
    return DocumentFactory(kind=Document.IMAGE)


@pytest.fixture()
def video():
    return DocumentFactory(kind=Document.VIDEO)


@pytest.fixture()
def pdf():
    return DocumentFactory(kind=Document.PDF)


@pytest.fixture()
def audio():
    return DocumentFactory(kind=Document.AUDIO)


@pytest.fixture()
def text():
    return DocumentFactory(kind=Document.TEXT)


@pytest.fixture()
def other():
    return DocumentFactory(kind=Document.OTHER)
