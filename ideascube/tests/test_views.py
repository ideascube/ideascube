# -*- coding: utf-8 -*-
import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils import translation

from ideascube.views import validate_url

from ideascube.blog.tests.factories import ContentFactory
from ideascube.blog.models import Content
from ideascube.library.tests.factories import BookSpecimenFactory

from .factories import UserFactory
from ..views import ByTag, UserList

import mock

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


def test_home_page_should_redirect_to_welcome_staff_if_no_staff(app, user):
    response = app.get(reverse('index')).follow()
    assert response.status_code == 200
    assert response.forms['model_form']


def test_home_page_should_not_redirect_if_staff_exists(app, staffuser):
    app.get(reverse('index'), status=200)


def test_welcome_staff_should_redirect_to_home_page_if_staff_exists(staffapp):
    response = staffapp.get(reverse('welcome_staff'))
    assert response.status_code == 302


def test_welcome_page_should_create_staff_user_on_POST(app):
    form = app.get(reverse('welcome_staff')).forms['model_form']
    form['serial'] = 'myuser'
    form['password'] = 'password'
    form['password_confirm'] = 'password'
    form.submit().follow()
    user = user_model.objects.last()
    assert user.is_staff


def test_welcome_page_should_create_staff_user_with_unicode(app):
    form = app.get(reverse('welcome_staff')).forms['model_form']
    name = 'كتبه'
    form['serial'] = name
    form['password'] = 'password'
    form['password_confirm'] = 'password'
    response = form.submit().follow().follow()
    response.mustcontain(name.encode())


def test_welcome_page_does_not_create_staff_user_passwords_do_not_match(app):
    form = app.get(reverse('welcome_staff')).forms['model_form']
    form['serial'] = 'myuser'
    form['password'] = 'password1'
    form['password_confirm'] = 'password2'
    res = form.submit()
    assert 'The two passwords do not match' in res.unicode_body
    assert user_model.objects.count() == 0


def test_login_page_should_log_in_user_if_POST_data_is_correct(client, user,
                                                               staffuser):
    # Loading staffuser fixture so we don't fail into welcome_staff page.
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


def test_system_user_cannot_log_in(client, systemuser):
    response = client.post(reverse('login'), {
        'username': systemuser.serial,
        'password': systemuser.password,
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 0
    assert not response.context['user'].is_authenticated()


def test_login_from_link_should_redirect_to_previous(app, user, staffuser):
    # Loading staffuser fixture so we don't fail into welcome_staff page.
    mediacenter = app.get(reverse('mediacenter:index'))
    login = mediacenter.click('log in')
    form = login.forms['login']
    form['username'] = user.serial
    form['password'] = 'password'
    resp = form.submit()
    assert resp['Location'].endswith(reverse('mediacenter:index'))


def test_user_list_page_should_not_be_accessible_to_anonymous(app):
    assert app.get(reverse('user_list'), status=302)


def test_non_staff_should_not_access_user_list_page(loggedapp):
    assert loggedapp.get(reverse('user_list'), status=302)


def test_user_list_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(reverse('user_list'), status=200)
    response.mustcontain(str(user))


def test_system_user_does_not_appear_in_list(staffapp, systemuser):
    response = staffapp.get(reverse('user_list'), status=200)
    response.mustcontain(no=str(systemuser))


def test_user_list_page_is_paginated(staffapp, monkeypatch):
    monkeypatch.setattr(UserList, 'paginate_by', 2)
    UserFactory.create_batch(size=3)  # There is also the staff user.
    response = staffapp.get(reverse('user_list'))
    # Count should be the full count, not only current page total.
    assert response.pyquery.find('caption')[0].text == 'Users (4)'
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
    response.mustcontain(str(user1), no=str(user2))


def test_system_user_is_not_searchable(staffapp, systemuser):
    response = staffapp.get(reverse('user_list') + '?q=system')
    response.mustcontain(no=str(systemuser))


def test_user_detail_page_should_not_be_accessible_to_anonymous(app, user):
    assert app.get(reverse('user_detail', kwargs={'pk': user.pk}),
                   status=302)


def test_non_staff_should_not_access_user_detail_page(loggedapp, user):
    assert loggedapp.get(reverse('user_detail', kwargs={'pk': user.pk}),
                         status=302)


def test_user_detail_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(reverse('user_detail', kwargs={'pk': user.pk}))
    response.mustcontain(str(user))


def test_system_user_cannot_be_viewed(staffapp, systemuser):
    response = staffapp.get(
        reverse('user_detail', kwargs={'pk': systemuser.pk}), status=404)


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


def test_system_serial_is_unique(staffapp, systemuser):
    form = staffapp.get(reverse('user_create')).forms['model_form']
    form['serial'] = systemuser.serial
    response = form.submit()
    assert response.status_code == 200


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


def test_system_user_cannot_be_updated(staffapp, systemuser):
    url = reverse('user_update', kwargs={'pk': systemuser.pk})
    form = staffapp.get(url, status=404)


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


def test_system_user_cannot_be_deleted(staffapp, systemuser):
    staffapp.get(
        reverse('user_delete', kwargs={'pk': systemuser.pk}),
        status=404)


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
    response = staffapp.get(url)
    response.mustcontain(str(user))
    form = response.forms['set_password']
    password = 'thisisanewpassword'
    form['new_password1'] = password
    form['new_password2'] = password
    form.submit().follow()
    assert user_model.objects.get(pk=user.pk).password != old_password


def test_systemuser_cannot_have_its_password_changed(staffapp, systemuser):
    staffapp.get(
        reverse('user_set_password', kwargs={'pk': systemuser.pk}),
        status=404)


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
    resp.mustcontain(
        'serial', user1.serial, user2.serial, no=[
            'usual name', user1.short_name, user2.short_name,
            'full_name', user1.full_name, user2.full_name,
            ])


def test_export_users_should_be_ok_in_arabic(staffapp, settings):
    translation.activate('ar')
    user1 = UserFactory(serial="جبران خليل جبران")
    user2 = UserFactory(serial="النبي (كتاب)")
    resp = staffapp.get(reverse('user_export'), status=200)
    field = user_model._meta.get_field('serial')
    resp.mustcontain(str(field.verbose_name))
    resp.mustcontain(user1.serial)
    resp.mustcontain(user2.serial)
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
    assert 'Example Domain' in response.content.decode()
    assert "Vary" not in response.headers


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = ContentFactory(status=Content.PUBLISHED, tags=['plane'])
    boat = ContentFactory(status=Content.PUBLISHED, tags=['boat'])
    plane2 = BookSpecimenFactory(book__tags=['plane'])
    boat2 = BookSpecimenFactory(book__tags=['boat'])
    response = app.get(reverse('by_tag'), {'tags': 'plane'})
    assert plane.title in response.content.decode()
    assert plane2.book.title in response.content.decode()
    assert boat.title not in response.content.decode()
    assert boat2.book.title not in response.content.decode()


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(ByTag, 'paginate_by', 2)
    ContentFactory.create_batch(size=2, status=Content.PUBLISHED,
                                tags=['plane'])
    BookSpecimenFactory.create_batch(size=2, book__tags=['plane'])
    url = reverse('by_tag')
    url = url+"?tags=plane"
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '&page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '&page=3', status=404)


def test_build_package_card_info_must_not_fail_for_no_package(app, systemuser):
    from ideascube.configuration import set_config
    from ideascube.views import build_package_card_info
    set_config('home-page', 'displayed-package-ids', ['test.package1'], systemuser)
    assert build_package_card_info() == []


def test_build_package_card_info(app, systemuser, catalog):
    from ideascube.configuration import set_config
    from ideascube.views import build_package_card_info
    from ideascube.serveradmin.catalog import ZippedZim, ZippedMedias
    catalog.add_mocked_package(ZippedZim('test.package1.fr', {
        'name':'Test package1',
        'description':'Test package1 description',
        'language':'fr',
        'staff_only':False}))
    catalog.add_mocked_package(ZippedMedias('test.package2.fr', {
        'name':'Test package2',
        'description':'Test package2 description',
        'language':'fr',
        'staff_only':False}))
    set_config('home-page', 'displayed-package-ids', ['test.package1.fr', 'test.package2.fr'], systemuser)

    assert build_package_card_info() == [{
        'package_id' : 'test.package1.fr',
        'name'       : 'Test package1',
        'description': 'Test package1 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'kiwix',
        'css_class'  : 'test.package1',
        'theme'      : 'learn'
    },
    {
        'package_id' : 'test.package2.fr',
        'name'       : 'Test package2',
        'description': 'Test package2 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'media-package',
        'css_class'  : None,
        'theme'      : None
    }]


@pytest.mark.usefixtures('staffuser')
def test_cards_properly_displayed(app):
    with mock.patch('ideascube.views.build_package_card_info') as Mocker:
        Mocker.return_value = [{
            'package_id' : 'wikipedia.fr',
            'name'       : 'Test package1',
            'description': 'Test package1 description',
            'lang'       : 'fr',
            'is_staff'   : False,
            'id'         : 'kiwix'
        }]
        response = app.get(reverse('index'), status=200)
        assert 'Test package1' in response.unicode_body
