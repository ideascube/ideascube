import pytest
import django_webtest

from django.core.urlresolvers import reverse

from ideasbox.tests.factories import UserFactory


@pytest.fixture()
def user():
    return UserFactory(short_name="Hello", password='password')


@pytest.fixture()
def staffuser():
    return UserFactory(short_name="Hello", password='password', is_staff=True)


@pytest.fixture()
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture()
def loggedapp(app, user):
    """Return an app with an already logged in user."""
    form = app.get(reverse('login')).forms['login']
    form['username'] = user.serial
    form['password'] = 'password'
    form.submit().follow()
    setattr(app, 'user', user)  # for later use, if needed
    return app


@pytest.fixture()
def staffapp(app, staffuser):
    """Return an app with an already logged in staff user."""
    form = app.get(reverse('login')).forms['login']
    form['username'] = staffuser.serial
    form['password'] = 'password'
    form.submit().follow()
    setattr(app, 'user', user)  # for later use, if needed
    return app
