import pytest
import django_webtest
import os
import mock

from django.core.urlresolvers import reverse

from ideascube.tests.factories import UserFactory
from ideascube.search.utils import create_index_table


from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

import logging
# This Handler always use sys.stderr and do not cache it.
# Let's configure logging to always use it when we are testing.
_alwaysUseStdErrHandler = logging._StderrHandler(logging.WARNING)
logging.basicConfig(handlers=[_alwaysUseStdErrHandler])


@pytest.fixture()
def cleansearch():
    create_index_table(force=True)


@pytest.fixture()
def user(db):
    return UserFactory(serial='123456',
                       short_name="Hello",
                       password='password')


@pytest.fixture()
def staffuser(db):
    return UserFactory(serial='123456staff',
                       short_name="Hello",
                       password='password',
                       is_staff=True)


@pytest.fixture()
def systemuser(db):
    from django.contrib.auth import get_user_model
    # Create it the same way the migration does it
    User = get_user_model()
    try:
        return User.objects.get_system_user()
    except User.DoesNotExist:
        return UserFactory(serial='__system__',
                           full_name='System',
                           password='!!')


@pytest.fixture
def setup_dirs(monkeypatch, tmpdir, settings):
    storage_root = tmpdir.mkdir('storage')
    settings.STORAGE_ROOT = storage_root.strpath
    settings.BACKUPED_ROOT = storage_root.mkdir('main').strpath
    settings.MEDIA_ROOT = storage_root.mkdir('main', 'media').strpath
    settings.CATALOG_STORAGE_ROOT = storage_root.mkdir(
        'main', 'catalog').strpath

    cache_root = tmpdir.mkdir('cache')
    settings.CATALOG_CACHE_ROOT = cache_root.mkdir('catalog').strpath

    install_root = tmpdir.mkdir('installs')
    settings.CATALOG_HANDLER_INSTALL_DIR = (
        install_root.mkdir('handler').strpath)
    settings.CATALOG_KIWIX_INSTALL_DIR = (
        install_root.mkdir('kiwix').strpath)
    settings.CATALOG_MEDIACENTER_INSTALL_DIR = (
        install_root.mkdir('mediacenter').strpath)
    settings.CATALOG_NGINX_INSTALL_DIR = (
        install_root.mkdir('nginx').strpath)

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
    form.submit()
    setattr(app, 'user', user)  # for later use, if needed
    return app


@pytest.fixture()
def staffapp(app, staffuser):
    """Return an app with an already logged in staff user."""
    form = app.get(reverse('login')).forms['login']
    form['username'] = staffuser.serial
    form['password'] = 'password'
    form.submit()
    setattr(app, 'user', staffuser)  # for later use, if needed
    return app


@pytest.fixture()
def testdatadir(request):
    datadir = request.fspath.dirpath().join('data')

    assert datadir.check(dir=True)
    return datadir


def pytest_configure(config):
    from django.conf import settings

    # This is already supposed to be the case by default, and we even tried
    # setting it explicitly anyway.
    #
    # But somehow, at the very beginning of the test suite (when running the
    # migrations or when the post_migrate signal is fired), the transient
    # database is on the filesystem (the value of NAME).
    #
    # We can't figure out why that is, it might be a bug in pytest-django, or
    # worse in django itself.
    #
    # Somehow the default database is always in memory, though.
    settings.DATABASES['transient']['TEST_NAME'] = ':memory:'

    # The documentation says not to use the ManifestStaticFilesStorage for
    # tests, and indeed if we do they fail.
    settings.STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage.StaticFilesStorage')

class CatalogMocker:
    """A CatalogMocker.
    A instance of CatalogMocker is a (reusable) context manager.
    """
    def __init__(self):
        self.patcher = mock.patch('ideascube.serveradmin.catalog.Catalog',
                                  spec=True)
        self.packages = []
        self.mocked = None

    def add_mocked_package(self, package):
        self.packages.append(package)

    def list_installed(self, ids_list):
        if '*' in ids_list:
            return self.packages

        return [p for p in self.packages if p.id in ids_list]

    def __enter__(self):
        if self.mocked is not None:
            raise RuntimeError(
                "CatalogMocker is not a reentrant context manager.\n"
                "You can open only one context at the same time "
                "and it seems that a context is already opened at this time.")

        self.mocked = self.patcher.__enter__()
        instance = self.mocked.return_value
        instance.list_installed.side_effect = self.list_installed
        return self.mocked

    def __exit__(self, type, value, traceback):
        self.patcher.__exit__(type, value, traceback)
        self.mocked = None


@pytest.yield_fixture()
def catalog():
    mocker = CatalogMocker()
    with mocker:
        yield mocker


class Migrator:
    def __init__(self, migrate_from, migrate_to):
        self.migrate_from = migrate_from
        self.migrate_to = migrate_to

        self.executor = MigrationExecutor(connection)
        self.executor.loader.build_graph()  # reload.
        self.executor.migrate(self.migrate_from)

    def run_migration(self):
        self.executor.loader.build_graph()  # reload.
        self.executor.migrate(self.migrate_to)

    @property
    def old_apps(self):
        return self.executor.loader.project_state(self.migrate_from).apps

    @property
    def new_apps(self):
        return self.executor.loader.project_state(self.migrate_to).apps


@pytest.fixture(scope='function')
def migration(db, request):
    migrate_from, migrate_to = request.param
    return Migrator(migrate_from, migrate_to)
