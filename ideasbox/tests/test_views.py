import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

pytestmark = pytest.mark.django_db
user_model = get_user_model()


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


def test_user_list_page_should_be_accessible(client, user):
    response = client.get(reverse('user_list'))
    assert response.status_code == 200
    assert unicode(user) and unicode(user) in response.content


def test_user_detail_page_should_be_accessible(client, user):
    response = client.get(reverse('user_detail', kwargs={'pk': user.pk}))
    assert response.status_code == 200
    assert unicode(user) and unicode(user) in response.content


def test_user_create_page_should_not_be_accessible_to_anonymous(client):
    response = client.get(reverse('user_create'))
    assert response.status_code == 302


def test_non_staff_should_not_access_user_create_page(loggedclient, user):
    response = loggedclient.get(reverse('user_create'))
    assert response.status_code == 302


def test_user_create_page_should_be_accessible_to_staff(staffclient):
    response = staffclient.get(reverse('user_create'))
    assert response.status_code == 200


def test_should_create_user_with_serial_only(staffclient):
    assert len(user_model.objects.all()) == 1
    serial = '12345xz22'
    response = staffclient.post(reverse('user_create'), {
        'serial': serial
    }, follow=True)
    assert response.status_code == 200
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.filter(serial=serial)


def test_should_not_create_user_without_serial(staffclient):
    assert len(user_model.objects.all()) == 1
    response = staffclient.post(reverse('user_create'), {})
    assert response.status_code == 200
    assert len(user_model.objects.all()) == 1


def test_user_update_page_should_not_be_accessible_to_anonymous(client, user):
    response = client.get(reverse('user_update', kwargs={'pk': user.pk}))
    assert response.status_code == 302


def test_non_staff_should_not_access_user_update_page(loggedclient, user):
    response = loggedclient.get(reverse('user_update', kwargs={'pk': user.pk}))
    assert response.status_code == 302


def test_staff_should_access_user_update_page(staffclient, user):
    response = staffclient.get(reverse('user_update', kwargs={'pk': user.pk}))
    assert response.status_code == 200


def test_staff_should_be_able_to_update_user(staffclient, user):
    assert len(user_model.objects.all()) == 2
    url = reverse('user_update', kwargs={'pk': user.pk})
    short_name = 'Denis'
    response = staffclient.post(url, {
        'serial': user.serial,
        'short_name': short_name
    }, follow=True)
    assert response.status_code == 200
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.get(serial=user.serial).short_name == short_name


def test_should_not_update_user_without_serial(client, staffclient, user):
    url = reverse('user_update', kwargs={'pk': user.pk})
    response = staffclient.post(url, {
        'serial': '',
        'short_name': 'ABCDEF'
    })
    assert response.status_code == 200
    dbuser = user_model.objects.get(serial=user.serial)
    assert dbuser.short_name == user.short_name


def test_delete_page_should_not_be_reachable_to_anonymous(client, user):
    response = client.get(reverse('user_delete', kwargs={'pk': user.pk}))
    assert response.status_code == 302


def test_delete_page_should_not_be_reachable_to_non_staff(loggedclient, user):
    response = loggedclient.get(reverse('user_delete', kwargs={'pk': user.pk}))
    assert response.status_code == 302


def test_staff_user_should_access_confirm_delete_page(staffclient, user):
    response = staffclient.get(reverse('user_delete', kwargs={'pk': user.pk}))
    assert response.status_code == 200


def test_non_staff_user_cannot_delete_user(client, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    response = client.post(url, {'confirm': 'yes'})
    assert response.status_code == 302
    assert len(user_model.objects.all()) == 1


def test_anonymous_cannot_delete_user(loggedclient, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    response = loggedclient.post(url, {'confirm': 'yes'})
    assert response.status_code == 302
    assert len(user_model.objects.all()) == 1


def test_staff_user_can_delete_user(staffclient, user):
    assert len(user_model.objects.all()) == 2  # staff user and normal user
    url = reverse('user_delete', kwargs={'pk': user.pk})
    response = staffclient.post(url, {'confirm': 'yes'}, follow=True)
    assert response.status_code == 200
    assert len(user_model.objects.all()) == 1
