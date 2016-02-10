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
