import pytest

pytestmark = pytest.mark.django_db


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_anonymous_user_should_not_access_admin(client):
    response = client.get('/admin/')
    assert response.status_code == 302
    assert 'login' in response['Location']


def test_normal_user_should_not_access_admin(client, user):
    assert client.login(serial=user.serial, password='password')
    response = client.get('/admin/')
    assert response.status_code == 302
    assert 'login' in response['Location']


def test_staff_user_should_access_admin(client, staffuser):
    assert client.login(serial=staffuser.serial, password='password')
    response = client.get('/admin/')
    assert response.status_code == 200
