import pytest


from ideasbox.tests import UserFactory


@pytest.fixture(scope="function")
def user(request):
    return UserFactory(short_name="Hello", password='password')


@pytest.fixture(scope="function")
def staffuser(request):
    return UserFactory(short_name="Hello", password='password', is_staff=True)
