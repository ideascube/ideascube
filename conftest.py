import pytest
import django_webtest
import os

from django.core.urlresolvers import reverse

from ideascube.tests.factories import UserFactory


@pytest.fixture()
def user():
    return UserFactory(short_name="Hello", password='password')


@pytest.fixture()
def staffuser():
    return UserFactory(short_name="Hello", password='password', is_staff=True)


@pytest.yield_fixture()
def storage_dir(monkeypatch, tmpdir, settings):
    """Return a new temporary storage dir.
    Settings are also modified to point to the directory."""
    STORAGE_ROOT = settings.STORAGE_ROOT

    # Get the paths to changes and their original values.
    original_paths = (k for k in dir(settings.wrapped_object)
                      if k.isupper() and not k.startswith('__'))
    original_paths = (k for k in original_paths
                      if k.endswith('_ROOT') or k.endswith('_DIR'))
    original_paths = {k: getattr(settings, k) for k in original_paths}
    original_paths = {k: v for k, v in original_paths.items() if v}

    # Update paths replacing STORAGE_ROOT by tmpdir.
    for k, v in original_paths.items():
        rel_path = os.path.relpath(v, STORAGE_ROOT)
        new_temp_path = os.path.join(str(tmpdir), rel_path)
        os.makedirs(new_temp_path, exist_ok=True)
        setattr(settings, k, new_temp_path)

    # Change also the location of the default_storage as this is cached
    # and not updated when settings changed.
    monkeypatch.setattr(
        'django.core.files.storage.default_storage.location',
        settings.MEDIA_ROOT
    )
    monkeypatch.setattr(
        'django.core.files.storage.default_storage.base_location',
        settings.MEDIA_ROOT
    )

    yield str(tmpdir)


@pytest.yield_fixture()
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    yield django_webtest.DjangoTestApp()
    wtm._unpatch_settings()


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
    setattr(app, 'user', staffuser)  # for later use, if needed
    return app


@pytest.fixture()
def testdatadir(request):
    datadir = request.fspath.dirpath().join('data')

    assert datadir.check(dir=True)
    return datadir
