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


def test_login_page_should_return_form_in_GET_mode(app):
    response = app.get(reverse('login'), status=200)
    assert response.forms['login']


@pytest.mark.usefixtures('user')
def test_home_page_should_redirect_to_welcome_staff_if_no_staff(app):
    response = app.get(reverse('index'), status=302).follow(status=200)
    assert response.forms['model_form']


@pytest.mark.usefixtures('staffuser')
def test_home_page_should_not_redirect_if_staff_exists(app):
    app.get(reverse('index'), status=200)


def test_welcome_staff_should_redirect_to_home_page_if_staff_exists(staffapp):
    response = staffapp.get(reverse('welcome_staff'), status=302)
    assert response.location == '/'


def test_welcome_page_should_create_staff_user_on_POST(app):
    form = app.get(reverse('welcome_staff'), status=200).forms['model_form']
    form['serial'] = 'myuser'
    form['password'] = 'password'
    form['password_confirm'] = 'password'
    response = form.submit(302)
    assert response.location == '/'
    assert user_model.objects.count() == 1
    user = user_model.objects.last()
    assert user.is_staff


def test_welcome_page_should_create_staff_user_with_unicode(app):
    form = app.get(reverse('welcome_staff'), status=200).forms['model_form']
    name = 'كتبه'
    form['serial'] = name
    form['password'] = 'password'
    form['password_confirm'] = 'password'
    response = form.submit(status=302).follow(status=302).follow(status=200)
    response.mustcontain(name)
    assert user_model.objects.count() == 1
    user = user_model.objects.last()
    assert user.serial == name
    assert user.is_staff


def test_welcome_page_does_not_create_staff_user_passwords_do_not_match(app):
    form = app.get(reverse('welcome_staff'), status=200).forms['model_form']
    form['serial'] = 'myuser'
    form['password'] = 'password1'
    form['password_confirm'] = 'password2'
    res = form.submit(status=200)
    assert 'The two passwords do not match' in res.text
    assert user_model.objects.count() == 0


@pytest.mark.usefixtures('staffuser')
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


def test_system_user_cannot_log_in(client, systemuser):
    response = client.post(reverse('login'), {
        'username': systemuser.serial,
        'password': systemuser.password,
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 0
    assert not response.context['user'].is_authenticated()


@pytest.mark.usefixtures('staffuser')
def test_login_from_link_should_redirect_to_previous(app, user):
    mediacenter = app.get(reverse('mediacenter:index'), status=200)
    login = mediacenter.click('log in')
    form = login.forms['login']
    form['username'] = user.serial
    form['password'] = 'password'
    resp = form.submit(status=302)
    assert resp.location.endswith(reverse('mediacenter:index'))


def test_user_list_page_should_not_be_accessible_to_anonymous(app):
    response = app.get(reverse('user_list'), status=302)
    assert '/login/?next=' in response.location


def test_non_staff_should_not_access_user_list_page(loggedapp):
    response = loggedapp.get(reverse('user_list'), status=302)
    assert '/login/?next=' in response.location


def test_user_list_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(reverse('user_list'), status=200)
    response.mustcontain(str(user))
    response.mustcontain(str(staffapp.user))


def test_system_user_does_not_appear_in_list(staffapp, systemuser):
    response = staffapp.get(reverse('user_list'), status=200)
    response.mustcontain(no=str(systemuser))


def test_user_list_page_is_paginated(staffapp, monkeypatch):
    monkeypatch.setattr(UserList, 'paginate_by', 2)
    UserFactory.create_batch(size=3)  # There is also the staff user.
    response = staffapp.get(reverse('user_list'), status=200)
    # Count should be the full count, not only current page total.
    assert response.pyquery.find('caption')[0].text == 'Users (4)'
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = staffapp.get(reverse('user_list') + '?page=2', status=200)
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    staffapp.get(reverse('user_list') + '?page=3', status=404)


def test_user_list_page_should_be_searchable(staffapp):
    user1 = UserFactory(full_name="user1")
    user2 = UserFactory(full_name="user2")
    response = staffapp.get(reverse('user_list') + '?q=user1', status=200)
    response.mustcontain(str(user1), no=str(user2))


def test_system_user_is_not_searchable(staffapp, systemuser):
    response = staffapp.get(reverse('user_list') + '?q=system')
    response.mustcontain(no=str(systemuser))


def test_user_detail_page_should_not_be_accessible_to_anonymous(app, user):
    response = app.get(
        reverse('user_detail', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_non_staff_should_not_access_user_detail_page(loggedapp, user):
    response = loggedapp.get(
        reverse('user_detail', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_user_detail_page_should_be_accessible_to_staff(staffapp, user):
    response = staffapp.get(
        reverse('user_detail', kwargs={'pk': user.pk}), status=200)
    response.mustcontain(str(user))


def test_system_user_cannot_be_viewed(staffapp, systemuser):
    staffapp.get(
        reverse('user_detail', kwargs={'pk': systemuser.pk}), status=404)


def test_user_create_page_should_not_be_accessible_to_anonymous(app):
    response = app.get(reverse('user_create'), status=302)
    assert '/login/?next=' in response.location


def test_non_staff_should_not_access_user_create_page(loggedapp, user):
    response = loggedapp.get(reverse('user_create'), status=302)
    assert '/login/?next=' in response.location


def test_should_create_user_with_serial_only(staffapp):
    assert user_model.objects.count() == 1
    serial = '12345xz22'
    form = staffapp.get(reverse('user_create'), status=200).forms['model_form']
    form['serial'] = serial
    form.submit()
    assert user_model.objects.count() == 2
    user_model.objects.get(serial=serial)


def test_should_not_create_user_without_serial(staffapp):
    assert user_model.objects.count() == 1
    form = staffapp.get(reverse('user_create'), status=200).forms['model_form']
    form.submit()
    assert user_model.objects.count() == 1


def test_system_serial_is_unique(staffapp, systemuser):
    assert user_model.objects.get_queryset_unfiltered().count() == 2
    form = staffapp.get(reverse('user_create'), status=200).forms['model_form']
    form['serial'] = systemuser.serial
    response = form.submit(status=200)
    assert response.request.path.endswith(reverse('user_create'))
    assert user_model.objects.get_queryset_unfiltered().count() == 2


def test_user_update_page_should_not_be_accessible_to_anonymous(app, user):
    response = app.get(
        reverse('user_update', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_non_staff_should_not_access_user_update_page(loggedapp, user):
    response = loggedapp.get(
        reverse('user_update', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_staff_should_be_able_to_update_user(staffapp, user):
    assert user_model.objects.count() == 2
    url = reverse('user_update', kwargs={'pk': user.pk})
    short_name = 'Denis'
    form = staffapp.get(url, status=200).forms['model_form']
    form['serial'] = user.serial
    form['short_name'] = short_name
    response = form.submit(status=302)
    assert response.location.endswith(
        reverse('user_detail', kwargs={'pk': user.pk}))
    assert user_model.objects.count() == 2
    assert user_model.objects.get(serial=user.serial).short_name == short_name


def test_should_not_update_user_without_serial(app, staffapp, user):
    url = reverse('user_update', kwargs={'pk': user.pk})
    form = staffapp.get(url, status=200).forms['model_form']
    form['serial'] = ''
    form['short_name'] = 'ABCDEF'
    assert form.submit()
    dbuser = user_model.objects.get(serial=user.serial)
    assert dbuser.short_name == user.short_name


def test_system_user_cannot_be_updated(staffapp, systemuser):
    url = reverse('user_update', kwargs={'pk': systemuser.pk})
    staffapp.get(url, status=404)


def test_anonymous_cannot_delete_user(app, user):
    assert user_model.objects.count() == 1
    response = app.get(
        reverse('user_delete', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location
    assert user_model.objects.count() == 1


def test_non_staff_cannot_delete_user(loggedapp, user):
    assert user_model.objects.count() == 1
    response = loggedapp.get(
        reverse('user_delete', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location
    assert user_model.objects.count() == 1


def test_staff_user_can_delete_user(staffapp, user):
    assert user_model.objects.count() == 2  # staff user and normal user
    url = reverse('user_delete', kwargs={'pk': user.pk})
    form = staffapp.get(url, status=200).forms['delete_form']
    form.submit()
    assert user_model.objects.count() == 1


def test_system_user_cannot_be_deleted(staffapp, systemuser):
    assert user_model.objects.get_queryset_unfiltered().count() == 2
    staffapp.get(
        reverse('user_delete', kwargs={'pk': systemuser.pk}), status=404)
    assert user_model.objects.get_queryset_unfiltered().count() == 2


def test_anonymous_cannot_access_toggle_staff_page(app, user):
    response = app.get(
        reverse('user_toggle_staff', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_logged_user_cannot_access_toggle_staff_page(loggedapp, user):
    response = loggedapp.get(
        reverse('user_toggle_staff', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_staff_can_toggle_user_is_staff_flag(staffapp, user):
    assert not user.is_staff
    url = reverse('user_toggle_staff', kwargs={'pk': user.pk})
    response = staffapp.get(url, status=302)
    assert response.location.endswith(
        reverse('user_detail', kwargs={'pk': user.pk}))
    assert user_model.objects.get(pk=user.pk).is_staff
    response = staffapp.get(url, status=302)
    assert response.location.endswith(
        reverse('user_detail', kwargs={'pk': user.pk}))
    assert not user_model.objects.get(pk=user.pk).is_staff


def test_anonymous_cannot_access_set_password_page(app, user):
    response = app.get(
        reverse('user_set_password', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_logged_user_cannot_access_set_password_page(loggedapp, user):
    response = loggedapp.get(
        reverse('user_set_password', kwargs={'pk': user.pk}), status=302)
    assert '/login/?next=' in response.location


def test_staff_can_set_password(staffapp, client, user):
    old_password = user.password
    url = reverse('user_set_password', kwargs={'pk': user.pk})
    response = staffapp.get(url, status=200)
    response.mustcontain(str(user))
    form = response.forms['set_password']
    password = 'thisisanewpassword'
    form['new_password1'] = password
    form['new_password2'] = password
    response = form.submit(status=302)
    assert response.location.endswith(
        reverse('user_detail', kwargs={'pk': user.pk}))
    dbuser = user_model.objects.get(pk=user.pk)
    assert dbuser.password != old_password
    assert dbuser.check_password(password)


def test_systemuser_cannot_have_its_password_changed(staffapp, systemuser):
    staffapp.get(
        reverse('user_set_password', kwargs={'pk': systemuser.pk}),
        status=404)


def test_anonymous_cannot_export_users(app, user):
    response = app.get(reverse('user_export'), status=302)
    assert '/login/?next=' in response.location


def test_logged_user_cannot_export_users(loggedapp, user):
    response = loggedapp.get(reverse('user_export'), status=302)
    assert '/login/?next=' in response.location


def test_export_users_should_return_csv_with_users(staffapp, settings):
    user1 = UserFactory(short_name="user1", full_name="I'm user1")
    user2 = UserFactory(short_name="user2", full_name=u"I'm user2 with é")
    resp = staffapp.get(reverse('user_export'), status=200)
    resp.mustcontain(
        'serial', user1.serial, user2.serial, no=[
            'short_name', user1.short_name, user2.short_name,
            'full_name', user1.full_name, user2.full_name,
            ])


def test_export_users_should_be_ok_in_arabic(staffapp, settings):
    translation.activate('ar')
    user1 = UserFactory(serial="جبران خليل جبران")
    user2 = UserFactory(serial="النبي (كتاب)")
    resp = staffapp.get(reverse('user_export'), status=200)
    resp.mustcontain('serial')
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
    assert 'Example Domain' in response.text
    assert "Vary" not in response.headers


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = ContentFactory(status=Content.PUBLISHED, tags=['plane'])
    boat = ContentFactory(status=Content.PUBLISHED, tags=['boat'])
    plane2 = BookSpecimenFactory(item__tags=['plane'])
    boat2 = BookSpecimenFactory(item__tags=['boat'])
    response = app.get(reverse('by_tag'), {'tags': 'plane'})
    assert plane.title in response.text
    assert plane2.item.name in response.text
    assert boat.title not in response.text
    assert boat2.item.name not in response.text


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(ByTag, 'paginate_by', 2)
    ContentFactory.create_batch(size=2, status=Content.PUBLISHED,
                                tags=['plane'])
    BookSpecimenFactory.create_batch(size=2, item__tags=['plane'])
    url = reverse('by_tag')
    url = url+"?tags=plane"
    response = app.get(url, status=200)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '&page=2', status=200)
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '&page=3', status=404)


def test_build_package_card_info_must_not_fail_for_no_package(systemuser):
    from ideascube.configuration import set_config
    from ideascube.views import build_package_card_info
    set_config('home-page', 'displayed-package-ids', ['test.package1'], systemuser)
    assert build_package_card_info() == []


def test_build_package_card_info(systemuser, catalog):
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
        assert 'Test package1' in response.text
