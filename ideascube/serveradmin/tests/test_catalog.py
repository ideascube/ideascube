import shutil

import pytest


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
def install_dir(tmpdir):
    return tmpdir.mkdir('install')


def fake_urlretrieve(url, path, reporthook=None):
    assert url.startswith('file://')

    src = url[7:]
    shutil.copyfile(src, path)


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
