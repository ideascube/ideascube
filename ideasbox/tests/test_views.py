import pytest

from django.core.urlresolvers import reverse

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


def test_login_page_should_return_form_in_GET_mode(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200


def test_login_page_should_log_in_user_if_POST_data_is_correct(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'password'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.context['user'].is_authenticated()


def test_login_page_should_not_log_in_user_with_incorrect_POST(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'passwordxxx'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 0
    assert not response.context['user'].is_authenticated()
