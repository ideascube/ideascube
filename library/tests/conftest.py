import pytest

from .factories import BookFactory, BookSpecimenFactory


@pytest.fixture()
def book():
    return BookFactory()


@pytest.fixture()
def specimen():
    return BookSpecimenFactory()
