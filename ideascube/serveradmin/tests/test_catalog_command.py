from operator import itemgetter
import zipfile

from django.core.management import call_command
from django.core.management.base import CommandError

from py.path import local as Path
import pytest
import yaml
import json

from ideascube.utils import URLRetrieveError, get_file_sha256


@pytest.fixture
def staticsite_path(tmpdir):
    path = tmpdir.mkdir('source').mkdir('packages').join('the-site')

    with zipfile.ZipFile(path.strpath, mode='w') as f:
        f.writestr('index.html', b'<html></html>')

    return path


def test_add_remote(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    expected = {
        'id': 'foo', 'name': 'Content from Foo',
        'url': 'file://{}'.format(remote_catalog_file.strpath),
        }

    call_command(
        'catalog', 'remotes', 'add', expected['id'], expected['name'],
        expected['url'])

    # Ensure the remote has been added
    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).join('remotes')

    assert remotes_dir.check(dir=True)
    assert remotes_dir.join('foo.json').check(file=True)

    with remotes_dir.join('foo.json').open('r') as f:
        assert json.load(f) == expected


def test_cannot_add_duplicate_remote(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    remote = {
        'id': 'foo', 'name': 'Content from Foo',
        'url': 'file://{}'.format(remote_catalog_file.strpath),
        }

    call_command(
        'catalog', 'remotes', 'add', remote['id'], remote['name'],
        remote['url'])

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).join('remotes')

    assert remotes_dir.check(dir=True)
    assert remotes_dir.join('foo.json').check(file=True)

    old_mtime = remotes_dir.join('foo.json').mtime()

    capsys.readouterr()

    # Adding a remote with the same id and url should be ignored
    call_command(
        'catalog', 'remotes', 'add', remote['id'], remote['name'],
        remote['url'])

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == 'This remote already exists, ignoring'

    # Adding a remote with a different id but the same url should fail
    with pytest.raises(CommandError) as excinfo:
        call_command(
            'catalog', 'remotes', 'add', remote['id'] + '2', remote['name'],
            remote['url'])

    excinfo.match('A remote with this url already exists')
    assert remotes_dir.join('foo2.json').check(exists=False)

    # Adding a remote with the same id but a different url should fail
    with pytest.raises(CommandError) as excinfo:
        call_command(
            'catalog', 'remotes', 'add', remote['id'], remote['name'],
            remote['url'] + "bad")

    excinfo.match('A remote with this id already exists')
    assert remotes_dir.join('foo.json').mtime() == old_mtime


def test_remove_remote(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    remote = {
        'id': 'foo', 'name': 'Content from Foo',
        'url': 'file://{}'.format(remote_catalog_file.strpath),
        }

    call_command(
        'catalog', 'remotes', 'add', remote['id'], remote['name'],
        remote['url'])
    call_command('catalog', 'remotes', 'remove', remote['id'])

    # Ensure the remote has been removed
    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).join('remotes')

    assert remotes_dir.check(dir=True)
    assert remotes_dir.listdir() == []


def test_cannot_remove_unexisting_remote():
    with pytest.raises(CommandError):
        call_command('catalog', 'remotes', 'remove', 'foo')


def test_list_no_remotes(capsys):
    call_command('catalog', 'remotes', 'list')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_add_then_list_multiple_remotes(tmpdir, capsys):
    remote_catalog_file1 = tmpdir.mkdir('source1').join('catalog.yml')
    remote_catalog_file1.write(
        'all:\n  foovideos:\n    name: Videos from Foo')
    remote_catalog_file2 = tmpdir.mkdir('source2').join('catalog.yml')
    remote_catalog_file2.write(
        'all:\n  barbooks:\n    name: Books from Bar')

    expected = [
        {
            'id': 'foo', 'name': 'Content from Foo',
            'url': 'file://{}'.format(remote_catalog_file1.strpath),
            },
        {
            'id': 'bar', 'name': 'Content from Bar',
            'url': 'file://{}'.format(remote_catalog_file2.strpath),
            },
        ]

    for remote in expected:
        call_command(
            'catalog', 'remotes', 'add', remote['id'], remote['name'],
            remote['url'])

    call_command('catalog', 'remotes', 'list')

    out, err = capsys.readouterr()
    assert out.strip('\n').split('\n') == [
        "             [{0[id]}] {0[name]} : {0[url]}".format(r)
        for r in sorted(expected, key=itemgetter('id'))
        ]
    assert err.strip() == ''


def test_add_then_remove_then_list_remote(tmpdir, capsys):
    remote_catalog_file = tmpdir.mkdir('source1').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    expected = {
        'id': 'foo', 'name': 'Content from Foo',
        'url': 'file://{}'.format(remote_catalog_file.strpath),
        }

    call_command(
        'catalog', 'remotes', 'add', expected['id'], expected['name'],
        expected['url'])
    call_command('catalog', 'remotes', 'remove', expected['id'])
    call_command('catalog', 'remotes', 'list')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_update_cache_without_remote(settings, capsys):
    expected = {}

    call_command('catalog', 'cache', 'update')

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    assert catalog_cache_dir.join('catalog.json').check(file=True)

    with catalog_cache_dir.join('catalog.json').open('r') as f:
        assert yaml.safe_load(f.read()) == expected

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_update_cache_with_remote(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))

    # Now let's say the remote published an update to their catalog
    remote_catalog_file = tmpdir.join('source', 'catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Great videos from Foo')

    call_command('catalog', 'cache', 'update')

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    assert catalog_cache_dir.join('catalog.json').check(file=True)

    expected = {'foovideos': {'name': 'Great videos from Foo'}}

    with catalog_cache_dir.join('catalog.json').open('r') as f:
        assert yaml.safe_load(f.read()) == expected

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_clear_metadata_cache(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    catalog_cache_path = catalog_cache_dir.join('catalog.json')
    downloaded_path = catalog_cache_dir.join('packages').join('foovideos')
    downloaded_path.write_binary(b'content')
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) != {}

    call_command('catalog', 'cache', 'clear', '--metadata')

    assert catalog_cache_dir.join('catalog.json').check(file=True)
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) == {}
    assert downloaded_path.read_binary() == b'content'

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_clear_package_cache(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    catalog_cache_path = catalog_cache_dir.join('catalog.json')
    downloaded_path = catalog_cache_dir.join('packages').join('foovideos')
    downloaded_path.write_binary(b'content')
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) != {}

    call_command('catalog', 'cache', 'clear', '--packages')

    assert catalog_cache_dir.join('catalog.json').check(file=True)
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) != {}
    assert downloaded_path.check(exists=False)

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_clear_cache(tmpdir, settings, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    catalog_cache_path = catalog_cache_dir.join('catalog.json')
    downloaded_path = catalog_cache_dir.join('packages').join('foovideos')
    downloaded_path.write_binary(b'content')
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) != {}

    call_command('catalog', 'cache', 'clear')

    assert catalog_cache_dir.join('catalog.json').check(file=True)
    assert yaml.safe_load(catalog_cache_path.read_text('utf-8')) == {}
    assert downloaded_path.check(exists=False)

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_split_cache(tmpdir, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    # Now write the catalog cache in the old format
    old_cache = yaml.dump({'installed': {}, 'available': {
        'foovideos': {'name': 'Videos from Foo'}}})

    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    catalog_storage_dir = Path(settings.CATALOG_STORAGE_ROOT)

    catalog_cache_dir.join('catalog.yml').write(old_cache)
    catalog_storage_dir.join('installed.json').remove()

    # And check that it migrates properly
    call_command('catalog', 'cache', 'update')

    expected = {
        'foovideos': {'name': 'Videos from Foo'},
        }
    assert yaml.safe_load(
        catalog_cache_dir.join('catalog.json').read()) == expected
    assert yaml.safe_load(
        catalog_storage_dir.join('installed.json').read()) == {}


def test_move_remotes(tmpdir, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(
        'all:\n  foovideos:\n    name: Videos from Foo')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))

    # Now move the remotes to the old location
    catalog_cache_dir = Path(settings.CATALOG_CACHE_ROOT)
    catalog_storage_dir = Path(settings.CATALOG_STORAGE_ROOT)

    catalog_storage_dir.join('remotes').move(catalog_cache_dir.join('remotes'))
    content = json.loads(catalog_cache_dir.join('remotes', 'foo.json').read())
    catalog_cache_dir.join('remotes', 'foo.yml').write(yaml.safe_dump(content))
    catalog_cache_dir.join('remotes', 'foo.json').remove()
    assert catalog_storage_dir.join('remotes').check(exists=False)

    # And check that it migrates properly
    call_command('catalog', 'cache', 'update')

    assert catalog_cache_dir.join('remotes').check(exists=False)
    assert catalog_storage_dir.join('remotes', 'foo.json').check(file=True)


def test_list_packages_without_remotes(capsys):
    call_command('catalog', 'list')

    out, err = capsys.readouterr()
    assert out.strip() == (
        "No remote sources configured, you won't see any available package.\n"
        "Add a remote source with:\n"
        "\n"
        "     catalog remotes add ID NAME URL")
    assert err.strip() == ''


def test_list_available_packages(tmpdir, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  foovideos:\n'
        '    name: Videos from Foo\n'
        '    version: 2017-06\n'
        '    size: 3027988\n'
        '    type: zipped-medias',
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    call_command('catalog', 'list', '--available')

    out, err = capsys.readouterr()
    assert out.strip() == (
        'Available packages\n'
        ' foovideos             2017-06       2.9 MB'
        '   zipped-medias   Videos from Foo')
    assert err.strip() == ''


def test_list_installed_packages(tmpdir, capsys, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  foovideos:\n'
        '    name: Videos from Foo\n'
        '    version: 2017-06\n'
        '    size: 3027988\n'
        '    type: zipped-medias',
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    # Pretend we installed something
    Path(settings.CATALOG_STORAGE_ROOT).join('installed.json').write_text(
        '{\n'
        '  "foovideos": {\n'
        '    "name": "Videos from Foo",\n'
        '    "version": "2017-06",\n'
        '    "size": 3027988,\n'
        '    "type": "zipped-medias"\n'
        '  }\n'
        '}\n',
        'utf-8')

    call_command('catalog', 'list', '--installed')

    out, err = capsys.readouterr()
    assert out.strip() == (
        'Installed packages\n'
        ' foovideos             2017-06       2.9 MB'
        '   zipped-medias   Videos from Foo')
    assert err.strip() == ''


def test_list_upgradable_packages(tmpdir, capsys, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  foovideos:\n'
        '    name: Videos from Foo\n'
        '    version: 2017-06\n'
        '    size: 3027988\n'
        '    type: zipped-medias',
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    # Pretend we installed something which has since been updated in the remote
    Path(settings.CATALOG_STORAGE_ROOT).join('installed.json').write_text(
        '{\n'
        '  "foovideos":{\n'
        '    "name": "Videos from Foo",\n'
        '    "version": "2017-05",\n'
        '    "size": 3027988,\n'
        '    "type": "zipped-medias"\n'
        '  }\n'
        '}\n',
        'utf-8')

    call_command('catalog', 'list', '--upgradable')

    out, err = capsys.readouterr()
    assert out.strip() == (
        'Available updates\n'
        ' foovideos             2017-06       2.9 MB'
        '   zipped-medias   Videos from Foo')
    assert err.strip() == ''


def test_list_no_upgradable_packages(tmpdir, capsys, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  foovideos:\n'
        '    name: Videos from Foo\n'
        '    version: 2017-06\n'
        '    size: 3027988\n'
        '    type: zipped-medias',
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    call_command('catalog', 'list', '--upgradable')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_list_upgradable_removed_from_remote(tmpdir, capsys, settings):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write_text('all: {}', 'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    # Pretend we installed something which has since disapeared from the remote
    Path(settings.CATALOG_STORAGE_ROOT).join('installed.yml').write_text(
        'foovideos:\n'
        '  name: Videos from Foo\n'
        '  version: 2017-05\n'
        '  size: 3027988\n'
        '  type: zipped-medias',
        'utf-8')

    call_command('catalog', 'list', '--upgradable')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_list_problematic_packages(tmpdir, capsys):
    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write('''all:
  foovideos:
    name: Videos from Foo
    type: UNKNOWNTYPE
    version: 0
    filesize: 0kb
  barvideos:
    name: Videos from Bar
    version: 0
    filesize: 0kb''')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    call_command('catalog', 'list')
    out, err = capsys.readouterr()
    assert err.strip() == ''
    assert out.strip() == ("Warning: Ignoring 2 unsupported package(s)\n"
                           "Use '--problems' for details.")

    call_command('catalog', 'list', '--problems')
    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ('Problematic packages\n'
                           'barvideos is missing a type\n'
                           'foovideos has an invalid type: UNKNOWNTYPE')


@pytest.mark.usefixtures('db', 'systemuser')
def test_install_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Installing the-site-2017-06'
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')
    assert not (package_cache / 'the-site-2017-06').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_install_package_and_keep_download(
        tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', '--keep-downloads', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Installing the-site-2017-06'
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')
    assert (package_cache / 'the-site-2017-06').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_install_package_already_in_extra_cache(
        tmpdir, capsys, settings, staticsite_path, mocker):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    extra_cache = tmpdir.mkdir('extra-cache')
    pre_downloaded = extra_cache.join('the-site-2017-06')
    pre_downloaded.write_binary(staticsite_path.read_binary())

    # Get urlretrieve to fail unconditionally, so that the test will fail if
    # it is called, which would imply the extra cache was not used.
    def fake_urlretrieve(*args, **kwargs):
        raise URLRetrieveError('failed', 'file://{staticsite_path}'.format(staticsite_path=staticsite_path))

    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    call_command(
        'catalog', 'install', '--package-cache', extra_cache.strpath,
        'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Installing the-site-2017-06'
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')


def test_install_unavailable_package(tmpdir, settings, staticsite_path):
    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text('all: {}', 'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    with pytest.raises(CommandError) as excinfo:
        call_command('catalog', 'install', 'the-site')

    assert 'No such package: the-site' in excinfo.exconly()
    assert install_dir.join('the-site').check(exists=False)


@pytest.mark.usefixtures('db', 'systemuser')
def test_remove_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'remove', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Removing the-site-2017-06'
    assert err.strip() == ''
    assert install_dir.join('the-site').check(exists=False)


def test_remove_uninstalled_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'remove', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == 'the-site is not installed'
    assert install_dir.join('the-site').check(exists=False)


@pytest.mark.usefixtures('db', 'systemuser')
def test_reinstall_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'reinstall', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-06')
    assert err.strip() == ''


@pytest.mark.usefixtures('db', 'systemuser')
def test_reinstall_package_and_keep_downloads(
        tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')
    assert not (package_cache / 'the-site-2017-06').exists()

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'reinstall', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-06')
    assert err.strip() == ''
    assert not (package_cache / 'the-site-2017-06').exists()

    call_command('catalog', 'reinstall', '--keep-downloads', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-06')
    assert err.strip() == ''
    assert (package_cache / 'the-site-2017-06').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_reinstall_unavailable_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')

    # The package was removed from the remote
    remote_catalog_file.write_text('all: {}', 'utf-8')
    call_command('catalog', 'cache', 'update')

    # Reset the output
    out, err = capsys.readouterr()

    with pytest.raises(CommandError) as excinfo:
        call_command('catalog', 'reinstall', 'the-site')

    assert 'No such package: the-site' in excinfo.exconly()


@pytest.mark.usefixtures('db', 'systemuser')
def test_reinstall_not_installed_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'reinstall', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Installing the-site-2017-06'
    assert err.strip() == 'the-site is not installed'
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')


@pytest.mark.usefixtures('db', 'systemuser')
def test_upgrade_package(tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')

    # The package was updated on the remote
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-07\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')
    call_command('catalog', 'cache', 'update')

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'upgrade')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-07')
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')


@pytest.mark.usefixtures('db', 'systemuser')
def test_upgrade_package_and_keep_downloads(
        tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')
    assert not (package_cache / 'the-site-2017-06').exists()

    # The package was updated on the remote
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-07\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')
    call_command('catalog', 'cache', 'update')

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'upgrade')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-07')
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')
    assert not (package_cache / 'the-site-2017-07').exists()

    # The package was again updated on the remote
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-08\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')
    call_command('catalog', 'cache', 'update')

    call_command('catalog', 'upgrade', '--keep-downloads')
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-07\n'
        'Installing the-site-2017-08')
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')
    assert (package_cache / 'the-site-2017-08').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_upgrade_package_already_in_extra_cache(
        tmpdir, capsys, settings, staticsite_path, mocker):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'install', 'the-site')

    # The package was updated on the remote
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-07\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')
    call_command('catalog', 'cache', 'update')

    extra_cache = tmpdir.mkdir('extra-cache')
    pre_downloaded = extra_cache.join('the-site-2017-07')
    pre_downloaded.write_binary(staticsite_path.read_binary())

    # Get urlretrieve to fail unconditionally, so that the test will fail if
    # it is called, which would imply the extra cache was not used.
    def fake_urlretrieve(*args, **kwargs):
        raise URLRetrieveError('failed', 'file://{staticsite_path}'.format(staticsite_path=staticsite_path))

    mocker.patch(
        'ideascube.serveradmin.catalog.urlretrieve',
        side_effect=fake_urlretrieve)

    # Reset the output
    out, err = capsys.readouterr()

    call_command('catalog', 'update', '--package-cache', extra_cache.strpath)
    out, err = capsys.readouterr()
    assert out.strip() == (
        'Removing the-site-2017-06\n'
        'Installing the-site-2017-07')
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')


def test_upgrade_unavailable_package(tmpdir, settings, staticsite_path):
    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text('all: {}', 'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    with pytest.raises(CommandError) as excinfo:
        call_command('catalog', 'upgrade', 'the-site')

    assert 'No such package: the-site' in excinfo.exconly()
    assert install_dir.join('the-site').check(exists=False)


@pytest.mark.usefixtures('db', 'systemuser')
def test_upgrade_not_installed_package(
        tmpdir, capsys, settings, staticsite_path):
    sha256sum = get_file_sha256(staticsite_path.strpath)

    remote_catalog_file = tmpdir.join('source').join('catalog.yml')
    remote_catalog_file.write_text(
        'all:\n'
        '  the-site:\n'
        '    name: A great web site\n'
        '    version: 2017-06\n'
        '    sha256sum: {sha256sum}\n'
        '    size: 3027988\n'
        '    url: file://{staticsite_path}\n'
        '    type: static-site'.format(sha256sum=sha256sum, staticsite_path=staticsite_path),
        'utf-8')

    call_command(
        'catalog', 'remotes', 'add', 'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    call_command('catalog', 'cache', 'update')

    install_dir = Path(settings.CATALOG_NGINX_INSTALL_DIR)
    assert install_dir.join('the-site').check(exists=False)

    call_command('catalog', 'upgrade', 'the-site')
    out, err = capsys.readouterr()
    assert out.strip() == 'Installing the-site-2017-06'
    assert err.strip() == ''
    assert install_dir.join('the-site').join('index.html').read_binary() == (
        b'<html></html>')
