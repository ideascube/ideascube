import os
from hashlib import sha256

import pytest
from resumable import DownloadCheck, DownloadError


@pytest.fixture(
    params=[
        {
            'id': 'foo',
            'name': 'Content provided by Foo',
            'url': 'http://foo.fr/catalog.yml',
        },
        {
            'name': 'Content provided by Foo',
            'url': 'http://foo.fr/catalog.yml',
        },
        {
            'id': 'foo',
            'url': 'http://foo.fr/catalog.yml',
        },
        {
            'id': 'foo',
            'name': 'Content provided by Foo',
        },
    ],
    ids=[
        'foo',
        'missing-id',
        'missing-name',
        'missing-url',
    ])
def input_file(tmpdir, request):
    path = tmpdir.join('foo.yml')

    if 'id' in request.param:
        path.write('id: {id}\n'.format(**request.param), mode='a')

    if 'name' in request.param:
        path.write('name: {name}\n'.format(**request.param), mode='a')

    if 'url' in request.param:
        path.write('url: {url}'.format(**request.param), mode='a')

    return {'path': path.strpath, 'input': request.param}


@pytest.fixture
def zippedzim_path(testdatadir, tmpdir):
    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = tmpdir.mkdir('packages').join('wikipedia.tum-2015-08')
    zippedzim.copy(path)

    return path


@pytest.fixture
def staticsite_path(testdatadir, tmpdir):
    zipfile = testdatadir.join('catalog', 'w2eu-2016-02-26')
    path = tmpdir.mkdir('packages').join('w2eu-2016-02-26')
    zipfile.copy(path)
    return path


@pytest.fixture
def install_dir(tmpdir):
    return tmpdir.mkdir('install')


# This is starting to look a lot like adding file:// support to
# resumable.urlretrieve...
# TODO: Do they want it upstream?
def fake_urlretrieve(url, path, reporthook=None, sha256sum=None):
    assert url.startswith('file://')

    src = url[7:]

    with open(src, 'rb') as in_, open(path, 'a+b') as out:
        out.seek(0)
        already = len(out.read())

        in_.seek(already)
        out.seek(already)
        out.write(in_.read())

    if sha256sum is not None:
        with open(path, 'rb') as f:
            checksum = sha256(f.read()).hexdigest()

        if sha256sum != checksum:
            raise DownloadError(DownloadCheck.checksum_mismatch)


def test_remote_from_file(input_file):
    from ideascube.serveradmin.catalog import InvalidFile, Remote

    path = input_file['path']
    expected_id = input_file['input'].get('id')
    expected_name = input_file['input'].get('name')
    expected_url = input_file['input'].get('url')

    if expected_id is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_file(path)

        assert 'id' in exc.exconly()

    elif expected_name is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_file(path)

        assert 'name' in exc.exconly()

    elif expected_url is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_file(path)

        assert 'url' in exc.exconly()

    else:
        remote = Remote.from_file(path)
        assert remote.id == expected_id
        assert remote.name == expected_name
        assert remote.url == expected_url


def test_remote_to_file(tmpdir):
    from ideascube.serveradmin.catalog import Remote

    path = tmpdir.join('foo.yml')

    remote = Remote(
        'foo', 'Content provided by Foo', 'http://foo.fr/catalog.yml')
    remote.to_file(path.strpath)

    lines = path.readlines(cr=False)
    lines = filter(lambda x: len(x), lines)
    lines = sorted(lines)

    assert lines == [
        'id: foo', 'name: Content provided by Foo',
        'url: http://foo.fr/catalog.yml']


def test_package():
    from ideascube.serveradmin.catalog import Package

    p = Package('wikipedia.fr', {
        'name': 'Wikipédia en français', 'version': '2015-08'})
    assert p.id == 'wikipedia.fr'
    assert p.name == 'Wikipédia en français'
    assert p.version == '2015-08'

    with pytest.raises(AttributeError):
        print(p.no_such_attribute)

    with pytest.raises(NotImplementedError):
        p.install('some-path', 'some-other-path')

    with pytest.raises(NotImplementedError):
        p.remove('some-path')


def test_package_without_version():
    from ideascube.serveradmin.catalog import Package

    p = Package('wikipedia.fr', {'name': 'Wikipédia en français'})
    assert p.id == 'wikipedia.fr'
    assert p.name == 'Wikipédia en français'
    assert p.version == '0'


def test_package_equality():
    from ideascube.serveradmin.catalog import Package

    p1 = Package('wikipedia.fr', {
        'name': 'Wikipédia en français', 'version': '2015-08',
        'type': 'zippedzim'})
    p2 = Package('wikipedia.en', {
        'name': 'Wikipédia en français', 'version': '2015-08',
        'type': 'zippedzim'})
    assert p1 != p2

    p3 = Package('wikipedia.fr', {
        'name': 'Wikipédia en français', 'version': '2015-09',
        'type': 'zippedzim'})
    assert p1 != p3

    p4 = Package('wikipedia.fr', {
        'name': 'Wikipédia en français', 'type': 'zippedzim',
        'version': '2015-08'})
    assert p1 == p4


def test_filesize_should_render_int_size_as_human_friendly():
    from ideascube.serveradmin.catalog import Package

    p = Package('wikipedia.fr', {'name': 'Wikipédia', 'size': 287325597})
    assert p.filesize == '274.0 MB'


def test_filesize_should_render_str_size_as_is():
    from ideascube.serveradmin.catalog import Package

    p = Package('wikipedia.fr', {'name': 'Wikipédia', 'size': '1.7 GB'})
    assert p.filesize == '1.7 GB'


def test_package_registry():
    from ideascube.serveradmin.catalog import Package

    # Ensure the base type itself is not added to the registry
    assert Package not in Package.registered_types.values()

    # Register a new package type, make sure it gets added to the registry
    class RegisteredPackage(Package):
        typename = 'tests-only'

    assert Package.registered_types['tests-only'] == RegisteredPackage

    # Define a new package type without a typename attribute, make sure it
    # does **not** get added to the registry
    class NotRegisteredPackage(Package):
        pass

    assert NotRegisteredPackage not in Package.registered_types.values()


def test_install_zippedzim(zippedzim_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    p.install(zippedzim_path.strpath, install_dir.strpath)

    data = install_dir.join('data')
    assert data.check(dir=True)

    content = data.join('content')
    assert content.check(dir=True)
    assert content.join('{}.zim'.format(p.id)).check(file=True)

    lib = data.join('library')
    assert lib.check(dir=True)
    assert lib.join('{}.zim.xml'.format(p.id)).check(file=True)

    index = data.join('index')
    assert index.check(dir=True)
    assert index.join('{}.zim.idx'.format(p.id)).check(dir=True)


def test_install_invalid_zippedzim(tmpdir, testdatadir, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim, InvalidFile

    src = testdatadir.join('backup', 'musasa-0.1.0-201501241620.tar')
    path = tmpdir.mkdir('packages').join('wikipedia.tum-2015-08')
    src.copy(path)

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})

    with pytest.raises(InvalidFile) as exc:
        p.install(path.strpath, install_dir.strpath)

    assert 'not a zip file' in exc.exconly()


def test_remove_zippedzim(zippedzim_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    p.install(zippedzim_path.strpath, install_dir.strpath)

    p.remove(install_dir.strpath)

    data = install_dir.join('data')
    assert data.check(dir=True)

    content = data.join('content')
    assert content.check(dir=True)
    assert content.join('{}.zim'.format(p.id)).check(exists=False)

    lib = data.join('library')
    assert lib.check(dir=True)
    assert lib.join('{}.zim.xml'.format(p.id)).check(exists=False)

    index = data.join('index')
    assert index.check(dir=True)
    assert index.join('{}.zim.idx'.format(p.id)).check(exists=False)


def test_install_staticsite(staticsite_path, install_dir):
    from ideascube.serveradmin.catalog import StaticSite

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    p.install(staticsite_path.strpath, install_dir.strpath)

    root = install_dir.join('w2eu')
    assert root.check(dir=True)

    index = root.join('index.html')
    with index.open() as f:
        assert 'static content' in f.read()


def test_remove_staticsite(staticsite_path, install_dir):
    from ideascube.serveradmin.catalog import StaticSite

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    p.install(staticsite_path.strpath, install_dir.strpath)

    p.remove(install_dir.strpath)

    root = install_dir.join('w2eu')
    assert root.check(exists=False)


def test_handler(tmpdir, settings):
    from ideascube.serveradmin.catalog import Handler

    settings.CATALOG_HANDLER_INSTALL_DIR = tmpdir.strpath
    h = Handler()
    assert h._install_dir == tmpdir.strpath


def test_kiwix_installs_zippedzim(tmpdir, settings, zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    settings.CATALOG_KIWIX_INSTALL_DIR = tmpdir.strpath

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)

    data = tmpdir.join('data')
    assert data.check(dir=True)

    content = data.join('content')
    assert content.check(dir=True)
    assert content.join('{}.zim'.format(p.id)).check(file=True)

    lib = data.join('library')
    assert lib.check(dir=True)
    assert lib.join('{}.zim.xml'.format(p.id)).check(file=True)

    index = data.join('index')
    assert index.check(dir=True)
    assert index.join('{}.zim.idx'.format(p.id)).check(dir=True)


def test_kiwix_does_not_fail_if_files_already_exist(tmpdir, settings,
                                                    zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    settings.CATALOG_KIWIX_INSTALL_DIR = tmpdir.strpath

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.install(p, zippedzim_path.strpath)

    data = tmpdir.join('data')
    assert data.check(dir=True)


def test_kiwix_removes_zippedzim(tmpdir, settings, zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    settings.CATALOG_KIWIX_INSTALL_DIR = tmpdir.strpath

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)

    h.remove(p)

    data = tmpdir.join('data')
    assert data.check(dir=True)

    content = data.join('content')
    assert content.check(dir=True)
    assert content.join('{}.zim'.format(p.id)).check(exists=False)

    lib = data.join('library')
    assert lib.check(dir=True)
    assert lib.join('{}.zim.xml'.format(p.id)).check(exists=False)

    index = data.join('index')
    assert index.check(dir=True)
    assert index.join('{}.zim.idx'.format(p.id)).check(exists=False)


def test_kiwix_commits_after_install(tmpdir, settings, zippedzim_path, mocker):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    settings.CATALOG_KIWIX_INSTALL_DIR = tmpdir.strpath
    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.commit()

    library = tmpdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata

    manager().get_service.assert_called_once_with('kiwix-server')
    manager().restart.assert_called_once()


def test_kiwix_commits_after_remove(tmpdir, settings, zippedzim_path, mocker):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim
    from ideascube.serveradmin.systemd import NoSuchUnit

    settings.CATALOG_KIWIX_INSTALL_DIR = tmpdir.strpath
    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    manager().get_service.side_effect = NoSuchUnit

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zim'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.commit()

    assert manager().get_service.call_count == 1
    manager().restart.assert_not_called()

    h.remove(p)
    h.commit()

    library = tmpdir.join('library.xml')
    assert library.check(exists=True)
    assert library.read_text('utf-8') == (
        "<?xml version='1.0' encoding='utf-8'?>\n<library/>")

    assert manager().get_service.call_count == 2
    manager().restart.assert_not_called()


def test_nginx_installs_zippedzim(tmpdir, settings, staticsite_path):
    from ideascube.serveradmin.catalog import Nginx, StaticSite

    settings.CATALOG_NGINX_INSTALL_DIR = tmpdir.strpath
    Nginx.root = os.path.join(settings.STORAGE_ROOT, 'nginx')

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    h = Nginx()
    h.install(p, staticsite_path.strpath)

    root = tmpdir.join('w2eu')
    assert root.check(dir=True)

    index = root.join('index.html')
    with index.open() as f:
        assert 'static content' in f.read()


def test_nginx_removes_zippedzim(tmpdir, settings, staticsite_path):
    from ideascube.serveradmin.catalog import Nginx, StaticSite

    settings.CATALOG_NGINX_INSTALL_DIR = tmpdir.strpath
    Nginx.root = os.path.join(settings.STORAGE_ROOT, 'nginx')

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    h = Nginx()
    h.install(p, staticsite_path.strpath)

    h.remove(p)

    root = tmpdir.join('w2eu')
    assert root.check(exists=False)


def test_nginx_commits_after_install(tmpdir, settings, staticsite_path,
                                     mocker, monkeypatch):
    from ideascube.serveradmin.catalog import Nginx, StaticSite

    settings.CATALOG_NGINX_INSTALL_DIR = tmpdir.strpath
    monkeypatch.setattr(Nginx, 'root', tmpdir.strpath)
    os.mkdir(tmpdir.join('sites-available').strpath)
    os.mkdir(tmpdir.join('sites-enabled').strpath)
    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    h = Nginx()
    h.install(p, staticsite_path.strpath)
    h.commit()

    conffile = tmpdir.join('sites-available', 'w2eu')
    with conffile.open() as f:
        assert 'server_name w2eu.' in f.read()
    symlink = tmpdir.join('sites-enabled', 'w2eu')
    assert symlink.check(exists=True)
    assert symlink.realpath() == conffile

    manager().get_service.assert_called_once_with('nginx')
    manager().restart.assert_called_once()


def test_nginx_commits_after_remove(tmpdir, settings, staticsite_path,
                                    mocker, monkeypatch):
    from ideascube.serveradmin.catalog import Nginx, StaticSite
    from ideascube.serveradmin.systemd import NoSuchUnit

    settings.CATALOG_NGINX_INSTALL_DIR = tmpdir.strpath
    monkeypatch.setattr(Nginx, 'root', tmpdir.strpath)
    os.mkdir(tmpdir.join('sites-available').strpath)
    os.mkdir(tmpdir.join('sites-enabled').strpath)
    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    manager().get_service.side_effect = NoSuchUnit

    p = StaticSite('w2eu', {
        'url': 'https://foo.fr/w2eu-2016-02-26.zim'})
    h = Nginx()
    h.install(p, staticsite_path.strpath)
    h.commit()

    assert manager().get_service.call_count == 1
    manager().restart.assert_not_called()

    h.remove(p)
    h.commit()

    conffile = tmpdir.join('sites-available', 'w2eu')
    assert conffile.check(exists=False)
    symlink = tmpdir.join('sites-enabled', 'w2eu')
    assert symlink.check(exists=False)

    assert manager().get_service.call_count == 2
    manager().restart.assert_not_called()


def test_catalog_no_remote(tmpdir, settings):
    from ideascube.serveradmin.catalog import Catalog

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    assert c.list_remotes() == []
    assert tmpdir.join('remotes').check(dir=True)
    assert tmpdir.join('remotes').listdir() == []


def test_catalog_existing_remote(tmpdir, settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    tmpdir.mkdir('remotes').join('foo.yml').write(
        'id: {id}\nname: {name}\nurl: {url}'.format(**params))

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    remotes = c.list_remotes()
    assert len(remotes) == 1

    remote = remotes[0]
    assert remote.id == params['id']
    assert remote.name == params['name']
    assert remote.url == params['url']


def test_catalog_add_remotes(tmpdir, settings):
    from ideascube.serveradmin.catalog import Catalog

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    c.add_remote('foo', 'Content provided by Foo', 'http://foo.fr/catalog.yml')
    remotes = c.list_remotes()
    assert len(remotes) == 1

    remote = remotes[0]
    assert remote.id == 'foo'
    assert remote.name == 'Content provided by Foo'
    assert remote.url == 'http://foo.fr/catalog.yml'

    c.add_remote('bar', 'Content provided by Bar', 'http://bar.fr/catalog.yml')
    remotes = c.list_remotes()
    assert len(remotes) == 2

    remote = remotes[0]
    assert remote.id == 'bar'
    assert remote.name == 'Content provided by Bar'
    assert remote.url == 'http://bar.fr/catalog.yml'

    remote = remotes[1]
    assert remote.id == 'foo'
    assert remote.name == 'Content provided by Foo'
    assert remote.url == 'http://foo.fr/catalog.yml'

    with pytest.raises(ValueError) as exc:
        c.add_remote('foo', 'Content by Foo', 'http://foo.fr/catalog.yml')

    assert 'foo' in exc.exconly()


def test_catalog_remove_remote(tmpdir, settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    tmpdir.mkdir('remotes').join('foo.yml').write(
        'id: {id}\nname: {name}\nurl: {url}'.format(**params))

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    c.remove_remote(params['id'])
    remotes = c.list_remotes()
    assert len(remotes) == 0

    with pytest.raises(ValueError) as exc:
        c.remove_remote(params['id'])

    assert params['id'] in exc.exconly()


def test_catalog_update_cache(tmpdir, settings, monkeypatch):
    from ideascube.serveradmin.catalog import Catalog

    monkeypatch.setattr(
        'ideascube.serveradmin.catalog.urlretrieve', fake_urlretrieve)

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    assert c._catalog == {'installed': {}, 'available': {}}

    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._catalog == {
        'installed': {},
        'available': {'foovideos': {'name': 'Videos from Foo'}}}

    c = Catalog()
    assert c._catalog == {
        'installed': {},
        'available': {'foovideos': {'name': 'Videos from Foo'}}}


def test_catalog_clear_cache(tmpdir, settings, monkeypatch):
    from ideascube.serveradmin.catalog import Catalog

    monkeypatch.setattr(
        'ideascube.serveradmin.catalog.urlretrieve', fake_urlretrieve)

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._catalog != {'installed': {}, 'available': {}}

    c.clear_cache()
    assert c._catalog == {'installed': {}, 'available': {}}


def test_catalog_install_package(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata


def test_catalog_install_package_glob(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata


def test_catalog_install_package_twice(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    spy_urlretrieve = mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    # Once to download the remote catalog.yml, once to download the package
    assert spy_urlretrieve.call_count == 2

    c.install_packages(['wikipedia.tum'])

    assert spy_urlretrieve.call_count == 2


def test_catalog_install_does_not_stop_on_failure(tmpdir, settings,
                                                  testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zip')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('  wikipedia.fr:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch('ideascube.serveradmin.catalog.urlretrieve',
                 side_effect=fake_urlretrieve)

    def fake_install(package, download_path):
        if package.id == 'wikipedia.tum':
            raise OSError

    spy_install = mocker.patch(
        'ideascube.serveradmin.catalog.Kiwix.install',
        side_effect=fake_install)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum', 'wikipedia.fr'])

    assert spy_install.call_count == 2
    assert 'wikipedia.tum' not in c._catalog['installed']
    assert 'wikipedia.fr' in c._catalog['installed']


def test_catalog_install_package_already_downloaded(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    packagesdir = cachedir.mkdir('packages')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(packagesdir.join('wikipedia.tum-2015-08'))

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    spy_urlretrieve = mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata

    # Once to download the remote catalog.yml
    assert spy_urlretrieve.call_count == 1


def test_catalog_install_package_already_in_additional_cache(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')
    additionaldir = tmpdir.mkdir('this-could-be-a-usb-stick')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(additionaldir.join('wikipedia.tum-2015-08'))

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    spy_urlretrieve = mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.add_package_cache(additionaldir.strpath)
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata

    # Once to download the remote catalog.yml
    assert spy_urlretrieve.call_count == 1


def test_catalog_install_package_partially_downloaded(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    packagesdir = cachedir.mkdir('packages')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    # Partially download the package
    packagesdir.join('wikipedia.tum-2015-08').write_binary(
        zippedzim.read_binary()[:100])

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata


def test_catalog_install_package_partially_downloaded_but_corrupted(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    packagesdir = cachedir.mkdir('packages')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    # Partially download the package
    packagesdir.join('wikipedia.tum-2015-08').write_binary(
        b'corrupt download')

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata


def test_catalog_install_package_does_not_exist(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog, NoSuchPackage

    cachedir = tmpdir.mkdir('cache')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(NoSuchPackage):
        c.install_packages(['nosuchpackage'])


def test_catalog_install_package_with_missing_type(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog, InvalidPackageMetadata

    cachedir = tmpdir.mkdir('cache')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    handler: kiwix\n')

    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(InvalidPackageMetadata):
        c.install_packages(['wikipedia.tum'])


def test_catalog_install_package_with_unknown_type(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog, InvalidPackageType

    cachedir = tmpdir.mkdir('cache')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: something-not-supported\n')
        f.write('    handler: kiwix\n')

    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(InvalidPackageType):
        c.install_packages(['wikipedia.tum'])


def test_catalog_remove_package(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])
    c.remove_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)
    assert library.read_text('utf-8') == (
        "<?xml version='1.0' encoding='utf-8'?>\n<library/>")


def test_catalog_remove_package_glob(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])
    c.remove_packages(['wikipedia.*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)
    assert library.read_text('utf-8') == (
        "<?xml version='1.0' encoding='utf-8'?>\n<library/>")


def test_catalog_update_package(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata
        assert 'date="2015-08-10"' in libdata

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-09')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-09.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-09\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: f8794e3c8676258b0b594ad6e464177dda8d66dbcbb04b301'
            'd78fd4c9cf2c3dd\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    c.update_cache()
    c.upgrade_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata
        assert 'date="2015-09-10"' in libdata


def test_catalog_update_package_glob(tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata
        assert 'date="2015-08-10"' in libdata

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-09')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-09.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-09\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: f8794e3c8676258b0b594ad6e464177dda8d66dbcbb04b301'
            'd78fd4c9cf2c3dd\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    c.update_cache()
    c.upgrade_packages(['wikipedia.*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="data/content/wikipedia.tum.zim"' in libdata
        assert 'indexPath="data/index/wikipedia.tum.zim.idx"' in libdata
        assert 'date="2015-09-10"' in libdata


def test_catalog_update_package_already_latest(
        tmpdir, settings, testdatadir, mocker, capsys):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')
    sourcedir = tmpdir.mkdir('source')

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = sourcedir.join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = sourcedir.join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    old_mtime = library.mtime()

    # Drop what was logged so far
    capsys.readouterr()

    c.upgrade_packages(['wikipedia.tum'])

    assert library.mtime() == old_mtime

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == 'wikipedia.tum has no update available'


def test_catalog_list_available_packages(tmpdir, settings, monkeypatch):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  foovideos:\n')
        f.write('    name: Videos from Foo\n')
        f.write('    type: zipped-zim\n')
        f.write('    version: 1.0.0\n')
        f.write('    size: 1GB\n')

    monkeypatch.setattr(
        'ideascube.serveradmin.catalog.urlretrieve', fake_urlretrieve)

    settings.CATALOG_CACHE_BASE_DIR = tmpdir.strpath
    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    pkgs = c.list_available(['nosuchpackage'])
    assert len(pkgs) == 0

    pkgs = c.list_available(['foovideos'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'foovideos'
    assert pkg.name == 'Videos from Foo'
    assert pkg.version == '1.0.0'
    assert pkg.size == '1GB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_available(['foo*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'foovideos'
    assert pkg.name == 'Videos from Foo'
    assert pkg.version == '1.0.0'
    assert pkg.size == '1GB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_available(['*videos'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'foovideos'
    assert pkg.name == 'Videos from Foo'
    assert pkg.version == '1.0.0'
    assert pkg.size == '1GB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_available(['*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'foovideos'
    assert pkg.name == 'Videos from Foo'
    assert pkg.version == '1.0.0'
    assert pkg.size == '1GB'
    assert isinstance(pkg, ZippedZim)


def test_catalog_list_installed_packages(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = tmpdir.mkdir('source').join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    pkgs = c.list_installed(['nosuchpackage'])
    assert len(pkgs) == 0

    pkgs = c.list_installed(['wikipedia.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-08'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['wikipedia.*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-08'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['*.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-08'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-08'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)


def test_catalog_list_upgradable_packages(
        tmpdir, settings, testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-08')
    path = tmpdir.mkdir('source').join('wikipedia_tum_all_nopic_2015-08.zim')
    zippedzim.copy(path)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-08\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    cachedir = tmpdir.mkdir('cache')
    installdir = tmpdir.mkdir('kiwix')

    settings.CATALOG_CACHE_BASE_DIR = cachedir.strpath
    settings.CATALOG_KIWIX_INSTALL_DIR = installdir.strpath

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])
    assert c.list_upgradable(['*']) == []

    zippedzim = testdatadir.join('catalog', 'wikipedia.tum-2015-09')
    path = tmpdir.join('source').join('wikipedia_tum_all_nopic_2015-09.zim')
    zippedzim.copy(path)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    with remote_catalog_file.open(mode='w') as f:
        f.write('all:\n')
        f.write('  wikipedia.tum:\n')
        f.write('    version: 2015-09\n')
        f.write('    size: 200KB\n')
        f.write('    url: file://{}\n'.format(path))
        f.write(
            '    sha256sum: 335d00b53350c63df45486c5433205f068ad90e33c208064b'
            '212c29a30109c54\n')
        f.write('    type: zipped-zim\n')
        f.write('    handler: kiwix\n')

    c.update_cache()
    pkgs = c.list_upgradable(['nosuchpackage'])
    assert len(pkgs) == 0

    pkgs = c.list_upgradable(['wikipedia.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-09'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['wikipedia.*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-09'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['*.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-09'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == '2015-09'
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)
