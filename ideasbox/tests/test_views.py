# -*- coding: utf-8 -*-
import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils import translation

from ideasbox.views import validate_url

from ideasbox.blog.tests.factories import ContentFactory
from ideasbox.blog.models import Content
from ideasbox.library.tests.factories import BookSpecimenFactory

from .factories import UserFactory
from ..views import ByTag, UserList

pytestmark = pytest.mark.django_db
user_model = get_user_model()


def test_home_page(app):
    assert app.get('/')


def test_anonymous_user_should_not_access_admin(app):
    response = app.get(reverse('admin:index'), status=302)
    assert 'login' in response['Location']


def test_normal_user_should_not_access_admin(loggedapp, user):
    response = loggedapp.get(reverse('admin:index'), status=302)
    assert 'login' in response['Location']


def test_staff_user_should_access_admin(staffapp):
    assert staffapp.get(reverse('admin:index'), status=200)


def test_login_page_should_return_form_in_GET_mode(app):
    assert app.get(reverse('login'), status=200)


def test_login_page_should_log_in_user_if_POST_data_is_correct(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'password'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.context['user'].is_authenticated()


def test_logged_users_are_logged_out_after_a_given_time(client, user):
    client.post(reverse('login'), {
        'username': user.serial,
        'password': 'password'
    }, follow=True)

    cookies = dict(client.cookies.items())
    sessionid = cookies['sessionid']
    # One hour currently defined by SESSION_COOKIE_AGE in conf/base.py
    assert dict(sessionid.items()).get('max-age') == 3600


def test_login_page_should_not_log_in_user_with_incorrect_POST(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'passwordxxx'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 0
    assert not response.context['user'].is_authenticated()


def test_user_list_page_should_not_be_accessible_to_anonymous(app):
    assert app.get(reverse('user_list'), status=302)


def test_non_staff_should_not_access_user_list_page(loggedapp):
    assert loggedapp.get(reverse('user_list'), status=302)


def test_user_list_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(reverse('user_list'), status=200)
    response.mustcontain(unicode(user))


def test_user_list_page_is_paginated(staffapp, monkeypatch):
    monkeypatch.setattr(UserList, 'paginate_by', 2)
    UserFactory.create_batch(size=3)  # There is also the staff user.
    response = staffapp.get(reverse('user_list'))
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = staffapp.get(reverse('user_list') + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = staffapp.get(reverse('user_list') + '?page=3', status=404)


def test_user_list_page_should_be_searchable(staffapp):
    user1 = UserFactory(full_name="user1")
    user2 = UserFactory(full_name="user2")
    response = staffapp.get(reverse('user_list') + '?q=user1')
    response.mustcontain(unicode(user1), no=unicode(user2))


def test_user_detail_page_should_not_be_accessible_to_anonymous(app, user):
    assert app.get(reverse('user_detail', kwargs={'pk': user.pk}),
                   status=302)


def test_non_staff_should_not_access_user_detail_page(loggedapp, user):
    assert loggedapp.get(reverse('user_detail', kwargs={'pk': user.pk}),
                         status=302)


def test_user_detail_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(reverse('user_detail', kwargs={'pk': user.pk}))
    response.mustcontain(unicode(user))


def test_user_create_page_should_not_be_accessible_to_anonymous(app):
    assert app.get(reverse('user_create'), status=302)


def test_non_staff_should_not_access_user_create_page(loggedapp, user):
    assert loggedapp.get(reverse('user_create'), status=302)


def test_user_create_page_should_be_accessible_to_staff(staffapp):
    assert staffapp.get(reverse('user_create'), status=200)


def test_should_create_user_with_serial_only(staffapp):
    assert len(user_model.objects.all()) == 1
    serial = '12345xz22'
    form = staffapp.get(reverse('user_create')).forms['model_form']
    form['serial'] = serial
    form.submit()
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.filter(serial=serial)


def test_should_not_create_user_without_serial(staffapp):
    assert len(user_model.objects.all()) == 1
    form = staffapp.get(reverse('user_create')).forms['model_form']
    form.submit()
    assert len(user_model.objects.all()) == 1


def test_user_update_page_should_not_be_accessible_to_anonymous(app, user):
    assert app.get(reverse('user_update', kwargs={'pk': user.pk}), status=302)


def test_non_staff_should_not_access_user_update_page(loggedapp, user):
    assert loggedapp.get(reverse('user_update', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_should_access_user_update_page(staffapp, user):
    assert staffapp.get(reverse('user_update', kwargs={'pk': user.pk}),
                        status=200)


def test_staff_should_be_able_to_update_user(staffapp, user):
    assert len(user_model.objects.all()) == 2
    url = reverse('user_update', kwargs={'pk': user.pk})
    short_name = 'Denis'
    form = staffapp.get(url).forms['model_form']
    form['serial'] = user.serial
    form['short_name'] = short_name
    form.submit().follow()
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.get(serial=user.serial).short_name == short_name


def test_should_not_update_user_without_serial(app, staffapp, user):
    url = reverse('user_update', kwargs={'pk': user.pk})
    form = staffapp.get(url).forms['model_form']
    form['serial'] = ''
    form['short_name'] = 'ABCDEF'
    assert form.submit()
    dbuser = user_model.objects.get(serial=user.serial)
    assert dbuser.short_name == user.short_name


def test_delete_page_should_not_be_reachable_to_anonymous(app, user):
    assert app.get(reverse('user_delete', kwargs={'pk': user.pk}), status=302)


def test_delete_page_should_not_be_reachable_to_non_staff(loggedapp, user):
    assert loggedapp.get(reverse('user_delete', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_user_should_access_confirm_delete_page(staffapp, user):
    assert staffapp.get(reverse('user_delete', kwargs={'pk': user.pk}),
                        status=200)


def test_anonymous_cannot_delete_user(app, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    url = reverse('user_delete', kwargs={'pk': user.pk})
    assert app.get(url, status=302)
    assert len(user_model.objects.all()) == 1


def test_non_staff_cannot_delete_user(loggedapp, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    assert loggedapp.get(url, status=302)
    assert len(user_model.objects.all()) == 1


def test_staff_user_can_delete_user(staffapp, user):
    assert len(user_model.objects.all()) == 2  # staff user and normal user
    url = reverse('user_delete', kwargs={'pk': user.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert len(user_model.objects.all()) == 1


def test_anonymous_cannot_access_toggle_staff_page(app, user):
    assert app.get(reverse('user_toggle_staff', kwargs={'pk': user.pk}),
                   status=302)
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_logged_user_cannot_access_toggle_staff_page(loggedapp, user):
    assert loggedapp.get(reverse('user_toggle_staff', kwargs={'pk': user.pk}),
                         status=302)
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_staff_can_access_toggle_staff_page(staffapp, user):
    assert staffapp.get(reverse('user_toggle_staff', kwargs={'pk': user.pk}),
                        status=302)
    assert user_model.objects.get(pk=user.pk).is_staff


def test_staff_can_toggle_user_is_staff_flag(staffapp, user):
    assert not user.is_staff
    url = reverse('user_toggle_staff', kwargs={'pk': user.pk})
    assert staffapp.get(url)
    assert user_model.objects.get(pk=user.pk).is_staff
    assert staffapp.get(url)
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_anonymous_cannot_access_set_password_page(app, user):
    assert app.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                   status=302)


def test_logged_user_cannot_access_set_password_page(loggedapp, user):
    assert loggedapp.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_can_access_set_password_page(staffapp, user):
    assert staffapp.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                        status=200)


def test_staff_can_set_password(staffapp, client, user):
    old_password = user.password
    url = reverse('user_set_password', kwargs={'pk': user.pk})
    form = staffapp.get(url).forms['set_password']
    password = 'thisisanewpassword'
    form['new_password1'] = password
    form['new_password2'] = password
    form.submit().follow()
    assert user_model.objects.get(pk=user.pk).password != old_password


def test_anonymous_cannot_export_users(app, user):
    assert app.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                   status=302)


def test_logged_user_cannot_export_users(loggedapp, user):
    assert loggedapp.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_can_export_users(staffapp, user):
    assert staffapp.get(reverse('user_set_password', kwargs={'pk': user.pk}),
                        status=200)


def test_export_users_should_return_csv_with_users(staffapp, settings):
    user1 = UserFactory(short_name="user1", full_name="I'm user1")
    user2 = UserFactory(short_name="user2", full_name=u"I'm user2 with é")
    resp = staffapp.get(reverse('user_export'), status=200)
    resp.mustcontain('created at')
    resp.mustcontain('full name')
    resp.mustcontain('serial')
    resp.mustcontain('usual name')
    resp.mustcontain(user1.short_name)
    resp.mustcontain(user1.full_name)
    resp.mustcontain(user2.short_name)
    resp.mustcontain(user2.full_name)


def test_export_users_should_be_ok_in_arabic(staffapp, settings):
    translation.activate('ar')
    user1 = UserFactory(short_name="user1", full_name=u"جبران خليل جبران")
    user2 = UserFactory(short_name="user2", full_name=u"النبي (كتاب)")
    resp = staffapp.get(reverse('user_export'), status=200)
    field, _, _, _ = user_model._meta.get_field_by_name('full_name')
    resp.mustcontain(unicode(field.verbose_name))
    resp.mustcontain(user1.short_name)
    resp.mustcontain(user1.full_name)
    resp.mustcontain(user2.short_name)
    resp.mustcontain(user2.full_name)
    translation.deactivate()


def build_request(target="http://example.org", verb="get", **kwargs):
    defaults = {
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
        'HTTP_REFERER': 'http://testserver/path/'
    }
    defaults.update(kwargs)
    func = getattr(RequestFactory(**defaults), verb)
    return func('/', {'url': target})


def test_good_request_passes():
    target = "http://osm.org/georss.xml"
    request = build_request(target)
    url = validate_url(request)
    assert url == target


def test_no_url_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request(""))


def test_relative_url_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request("/just/a/path/"))


def test_file_uri_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request("file:///etc/passwd"))


def test_localhost_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request("http://localhost/path/"))


def test_POST_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request(verb="post"))


def test_unkown_domain_raises():
    with pytest.raises(AssertionError):
        validate_url(build_request("http://xlkjdkjsdlkjfd.com"))


def test_valid_proxy_request(app):
    url = reverse('ajax-proxy')
    params = {'url': 'http://example.org'}
    headers = {
        'X_REQUESTED_WITH': 'XMLHttpRequest',
        'REFERER': 'http://testserver'
    }
    environ = {'SERVER_NAME': 'testserver'}
    response = app.get(url, params, headers, environ)
    assert response.status_code == 200
    assert 'Example Domain' in response.content
    assert "Vary" not in response.headers


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = ContentFactory(status=Content.PUBLISHED, tags=['plane'])
    boat = ContentFactory(status=Content.PUBLISHED, tags=['boat'])
    plane2 = BookSpecimenFactory(book__tags=['plane'])
    boat2 = BookSpecimenFactory(book__tags=['boat'])
    response = app.get(reverse('by_tag', kwargs={'tag': 'plane'}))
    assert plane.title in response.content
    assert plane2.book.title in response.content
    assert boat.title not in response.content
    assert boat2.book.title not in response.content


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(ByTag, 'paginate_by', 2)
    ContentFactory.create_batch(size=2, status=Content.PUBLISHED,
                                tags=['plane'])
    BookSpecimenFactory.create_batch(size=2, book__tags=['plane'])
    url = reverse('by_tag', kwargs={'tag': 'plane'})
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '?page=3', status=404)
