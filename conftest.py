import pytest


from ideasbox.tests.factories import UserFactory


@pytest.fixture()
def user():
    return UserFactory(short_name="Hello", password='password')


@pytest.fixture()
def staffuser():
    return UserFactory(short_name="Hello", password='password', is_staff=True)


@pytest.fixture()
def staffclient(client, staffuser):
    client.login(serial=staffuser.serial, password='password')
    return client


@pytest.fixture()
def loggedclient(client, user):
    client.login(serial=user.serial, password='password')
    return client
