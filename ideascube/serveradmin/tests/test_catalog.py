import os
from hashlib import sha256
import zipfile

from py.path import local as Path
import pytest
import yaml
import json

from ideascube.mediacenter.models import Document

@pytest.fixture(params=['yml', 'json'])
def input_type(request):
    return request.param


@pytest.fixture(params=[
    pytest.param({
        'id': 'foo',
        'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml',
    }, id='foo'),
    pytest.param({
        'id': 'bibliothèque',
        'name': 'Le contenu de la bibliothèque',
        'url': 'http://foo.fr/catalog.yml',
    }, id='utf8'),
    pytest.param({
        'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml',
    }, id='missing-id'),
    pytest.param({
        'id': 'foo',
        'url': 'http://foo.fr/catalog.yml',
    }, id='missing-name'),
    pytest.param({
        'id': 'foo',
        'name': 'Content provided by Foo',
    }, id='missing-url'),
])
def input_content(request):
    return request.param


@pytest.fixture
def input_file(tmpdir, input_type, input_content):
    path = tmpdir.join('foo.{}'.format(input_type))

    if input_type == 'yml':
       content = yaml.safe_dump(input_content)
    else:
       content = json.dumps(input_content)

    path.write_text(content, encoding='utf-8')

    return {'path': path.strpath, 'input': input_content}


class ZimfileInfo:
    def __init__(self, version, basename, source_path, sha256, zim_sha256):
        self.version = version
        self.basename = basename
        self.source_path = source_path
        self.sha256 = sha256
        self.zim_sha256 = zim_sha256

    def catalog_entry_dict(self):
        return {
            'version': self.version,
            'size': '200KB',
            'url': 'file://{}'.format(self.source_path),
            'sha256sum': self.sha256,
            'type': 'zipped-zim'
        }


@pytest.fixture
def sample_zim_package(testdatadir, tmpdir):
    basename = 'wikipedia_tum_all_nopic_2015-08.zip'
    orig_path = testdatadir.join('catalog', basename)
    sha256 = orig_path.computehash('sha256')
    source_path = tmpdir.ensure('source', dir=True).join(basename)
    orig_path.copy(source_path)
    zim_sha256 = \
        '8deddb6268c161ffad1f83e099fa5efd085f76eb80bc6aee7ad4eb8f12e0eb6c'
    return ZimfileInfo('2015-08', basename, source_path, sha256, zim_sha256)


@pytest.fixture
def sample_zim_package_09(testdatadir, tmpdir):
    basename = 'wikipedia_tum_all_nopic_2015-09.zip'
    orig_path = testdatadir.join('catalog', basename)
    sha256 = orig_path.computehash('sha256')
    source_path = tmpdir.ensure('source', dir=True).join(basename)
    orig_path.copy(source_path)
    zim_sha256 = \
        'd3d65b0c59c02966979b79743e844c053bb5e0b0a9e3edb2f9693d24321c22ae'
    return ZimfileInfo('2015-09', basename, source_path, sha256, zim_sha256)



@pytest.fixture
def zippedzim_path(testdatadir, tmpdir):
    zippedzim = testdatadir.join('catalog', 'wikipedia_tum_all_nopic_2015-08.zip')
    path = tmpdir.mkdir('packages').join('wikipedia_tum_all_nopic_2015-08.zip')
    zippedzim.copy(path)

    return path


@pytest.fixture
def staticsite_path(testdatadir, tmpdir):
    zipfile = testdatadir.join('catalog', 'w2eu-2016-02-26')
    path = tmpdir.mkdir('packages').join('w2eu-2016-02-26')
    zipfile.copy(path)
    return path


@pytest.fixture
def zippedmedia_path(testdatadir, tmpdir):
    zipfile = testdatadir.join('catalog', 'test-media.zip')
    path = tmpdir.mkdir('packages').join('test-media.zip')
    zipfile.copy(path)
    return path


@pytest.fixture
def install_dir(tmpdir):
    return tmpdir.mkdir('install')


def test_migration_from_yml(tmpdir):
    from ideascube.serveradmin.catalog import load_from_basepath
    data = {
        'a': {
            'vint': 4,
            'vstr': 'azerty',
            'vdate': '2014-11-30',
            'vsize': 1024
        },
        'b': {
            'vint': 5,
            'vstr': 'bépoè',
            'vdate': '2015-11-30.2',
            'vsize': '200MB'
        }
    }

    yml_file = tmpdir.join('foo.yml')
    yml_file.write(yaml.safe_dump(data))

    # After converting to json, int will be converted to str.
    data['a']['vint'] = '4'
    data['a']['vsize'] = '1024'
    data['b']['vint'] = '5'

    ret_data = load_from_basepath(str(tmpdir.join('foo')))

    assert ret_data == data
    assert yml_file.check(exists=False)
    assert tmpdir.join('foo.json').check(exists=True)

    # Be sure that we can read it again
    ret_data2 = load_from_basepath(str(tmpdir.join('foo')))
    assert ret_data2 == data


def test_migration_from_yml_wrong_date(tmpdir):
    from ideascube.serveradmin.catalog import load_from_basepath
    data = {'a': {'vdate': '2014-11-30'},
            'b': {'vdate': '2015-11-30'}
    }

    yml_file = tmpdir.join('foo.yml')
    yml_file.write(
        "a:\n"
        "  vdate: '2014-11-30'\n"
        "b:\n"
        "  vdate: 2015-11-30\n"
    )

    ret_data = load_from_basepath(str(tmpdir.join('foo')))

    assert ret_data == data
    assert yml_file.check(exists=False)
    assert tmpdir.join('foo.json').check(exists=True)

    # Be sure that we can read it again
    ret_data2 = load_from_basepath(str(tmpdir.join('foo')))
    assert ret_data2 == data


def test_migration_from_yml_broken_json(tmpdir):
    from ideascube.serveradmin.catalog import load_from_basepath
    data = {'a': {'vdate': '2014-11-30'},
            'b': {'vdate': '2015-11-30'}
    }

    yml_file = tmpdir.join('foo.yml')
    yml_file.write(
        "a:\n"
        "  vdate: '2014-11-30'\n"
        "b:\n"
        "  vdate: 2015-11-30\n"
    )

    json_file = tmpdir.join('foo.json')
    json_file.write(
        "{\n'"
        "  'a': {\n"
        "    'vdate': '2014-11-30'\n"
        "  }\n"
        "  'b': {\n"
        "    'vdate':"
    )

    ret_data = load_from_basepath(str(tmpdir.join('foo')))

    assert ret_data == data
    assert yml_file.check(exists=False)
    assert tmpdir.join('foo.json').check(exists=True)

    # Be sure that we can read it again
    ret_data2 = load_from_basepath(str(tmpdir.join('foo')))
    assert ret_data2 == data


def test_migration_from_yml_broken_json_and_no_yaml(tmpdir):
    from ideascube.serveradmin.catalog import load_from_basepath

    json_file = tmpdir.join('foo.json')
    json_file.write(
        "{\n'"
        "  'a': {\n"
        "    'vdate': '2014-11-30'\n"
        "  }\n"
        "  'b': {\n"
        "    'vdate':"
    )

    with pytest.raises(ValueError):
        load_from_basepath(str(tmpdir.join('foo')))

    assert json_file.check(exists=True)


def test_remote_from_file(input_file):
    from ideascube.serveradmin.catalog import InvalidFile, Remote

    basepath = os.path.splitext(input_file['path'])[0]
    expected_id = input_file['input'].get('id')
    expected_name = input_file['input'].get('name')
    expected_url = input_file['input'].get('url')

    if expected_id is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_basepath(basepath)

        assert 'id' in exc.exconly()

    elif expected_name is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_basepath(basepath)

        assert 'name' in exc.exconly()

    elif expected_url is None:
        with pytest.raises(InvalidFile) as exc:
            Remote.from_basepath(basepath)

        assert 'url' in exc.exconly()

    else:
        remote = Remote.from_basepath(basepath)
        assert remote.id == expected_id
        assert remote.name == expected_name
        assert remote.url == expected_url


def test_remote_to_file(tmpdir):
    from ideascube.serveradmin.catalog import Remote

    path = tmpdir.join('foo.json')
    basepath = os.path.splitext(path.strpath)[0]

    remote = Remote(
        'foo', 'Content provided by Foo', 'http://foo.fr/catalog.yml')
    remote.to_file(basepath)

    lines = path.readlines(cr=False)
    lines = lines[1:-1]
    lines = (l[:-1] if l.endswith(',') else l for l in lines)
    lines = filter(lambda x: len(x), lines)
    lines = sorted(lines)

    assert lines == [
        '  "id": "foo"',
        '  "name": "Content provided by Foo"',
        '  "url": "http://foo.fr/catalog.yml"']


def test_remote_to_file_utf8(tmpdir):
    from ideascube.serveradmin.catalog import Remote

    path = tmpdir.join('foo.json')
    basepath = os.path.splitext(path.strpath)[0]

    remote = Remote(
        'bibliothèque', 'Le contenu de la bibliothèque',
        'http://foo.fr/catalog.yml')
    remote.to_file(basepath)

    lines = path.read_text('utf-8').split('\n')
    lines = lines[1:-1]
    lines = (l[:-1] if l.endswith(',') else l for l in lines)
    lines = filter(lambda x: len(x), lines)
    lines = sorted(lines)

    assert lines == [
        '  "id": "biblioth\\u00e8que"',
        '  "name": "Le contenu de la biblioth\\u00e8que"',
        '  "url": "http://foo.fr/catalog.yml"']

    # Try loading it back
    remote = Remote.from_basepath(basepath)
    assert remote.id == 'bibliothèque'
    assert remote.name == 'Le contenu de la bibliothèque'


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


def test_install_zippedzim(zippedzim_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    p.install(zippedzim_path.strpath, install_dir.strpath)

    assert install_dir.join('{}.zim'.format(p.id)).check(file=True)
    assert install_dir.join('{}.zim.idx'.format(p.id)).check(dir=True)
    assert install_dir.join('{}.zim.json'.format(p.id)).check(file=True)


def test_install_invalid_zippedzim(tmpdir, testdatadir, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim, InvalidFile

    src = testdatadir.join('backup', 'musasa-0.1.0-201501241620.tar')
    path = tmpdir.mkdir('packages').join('wikipedia.tum-2015-08')
    src.copy(path)

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})

    with pytest.raises(InvalidFile) as exc:
        p.install(path.strpath, install_dir.strpath)

    assert 'not a zip file' in exc.exconly()


def test_remove_zippedzim(zippedzim_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    p.install(zippedzim_path.strpath, install_dir.strpath)

    p.remove(install_dir.strpath)

    assert install_dir.join('{}.zim'.format(p.id)).check(exists=False)
    assert install_dir.join('{}.zim.idx'.format(p.id)).check(exists=False)
    assert install_dir.join('{}.zim.json'.format(p.id)).check(exists=False)


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


@pytest.mark.usefixtures('db')
def test_install_zippedmedia(zippedmedia_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedMedias

    p = ZippedMedias('test-media', {
        'url': 'https://foo.fr/test-media.zip'})
    p.install(zippedmedia_path.strpath, install_dir.strpath)

    root = install_dir.join('test-media')
    assert root.check(dir=True)

    manifest = root.join('manifest.yml')
    assert manifest.exists()


@pytest.mark.usefixtures('db')
def test_install_zippedmedia_missing_manifest(tmpdir,
                                              zippedmedia_path,
                                              install_dir):
    from ideascube.serveradmin.catalog import (InvalidPackageContent,
                                               ZippedMedias)

    bad_zippedmedia_dir = tmpdir.mkdir('source')
    bad_zippedmedia_path = bad_zippedmedia_dir.join('bad-test-media.zip')

    with zipfile.ZipFile(zippedmedia_path.strpath) as orig, \
            zipfile.ZipFile(bad_zippedmedia_path.strpath, mode='w') as bad:
        names = filter(lambda n: n != 'manifest.yml', orig.namelist())

        for name in names:
            if name == 'manifest.yml':
                continue

            orig.extract(name, bad_zippedmedia_dir.strpath)
            bad.write(bad_zippedmedia_dir.join(name).strpath, arcname=name)
            bad_zippedmedia_dir.join(name).remove()

    with pytest.raises(InvalidPackageContent):
        p = ZippedMedias('test-media', {
            'url': 'https://foo.fr/bad-test-media.zip'})
        p.install(bad_zippedmedia_path.strpath, install_dir.strpath)


@pytest.mark.usefixtures('db')
def test_remove_zippedmedia(zippedmedia_path, install_dir):
    from ideascube.serveradmin.catalog import ZippedMedias

    p = ZippedMedias('test-media', {
        'url': 'https://foo.fr/test-media.zip'})
    p.install(zippedmedia_path.strpath, install_dir.strpath)

    p.remove(install_dir.strpath)

    root = install_dir.join('w2eu')
    assert root.check(exists=False)


def test_handler(settings):
    from ideascube.serveradmin.catalog import Handler

    h = Handler()
    assert h._install_dir == settings.CATALOG_HANDLER_INSTALL_DIR


def test_kiwix_installs_zippedzim(settings, zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)

    install_root = Path(settings.CATALOG_KIWIX_INSTALL_DIR)

    assert install_root.join('{}.zim'.format(p.id)).check(file=True)
    assert install_root.join('{}.zim.idx'.format(p.id)).check(dir=True)
    assert install_root.join('{}.zim.json'.format(p.id)).check(file=True)


def test_kiwix_does_not_fail_if_files_already_exist(settings, zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.install(p, zippedzim_path.strpath)

    install_root = Path(settings.CATALOG_KIWIX_INSTALL_DIR)

    data = install_root.join('data')
    assert data.check(dir=True)


def test_kiwix_removes_zippedzim(settings, zippedzim_path):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)

    h.remove(p)

    install_root = Path(settings.CATALOG_KIWIX_INSTALL_DIR)

    assert install_root.join('{}.zim'.format(p.id)).check(exists=False)
    assert install_root.join('{}.zim.idx'.format(p.id)).check(exists=False)
    assert install_root.join('{}.zim.json'.format(p.id)).check(exists=False)


def test_kiwix_commits_after_install(settings, zippedzim_path, mocker):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim

    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.commit()

    install_root = Path(settings.CATALOG_KIWIX_INSTALL_DIR)

    library = install_root.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    manager().get_service.assert_called_once_with('kiwix-server')
    manager().restart.call_count == 1


def test_kiwix_commits_after_remove(settings, zippedzim_path, mocker):
    from ideascube.serveradmin.catalog import Kiwix, ZippedZim
    from ideascube.serveradmin.systemd import NoSuchUnit

    manager = mocker.patch('ideascube.serveradmin.catalog.SystemManager')
    manager().get_service.side_effect = NoSuchUnit

    p = ZippedZim('wikipedia.tum', {
        'url': 'https://foo.fr/wikipedia_tum_all_nopic_2015-08.zip'})
    h = Kiwix()
    h.install(p, zippedzim_path.strpath)
    h.commit()

    assert manager().get_service.call_count == 1
    manager().restart.assert_not_called()

    h.remove(p)
    h.commit()

    install_root = Path(settings.CATALOG_KIWIX_INSTALL_DIR)

    library = install_root.join('library.xml')
    assert library.check(exists=True)
    assert library.read_text('utf-8') == (
        "<?xml version='1.0' encoding='utf-8'?>\n<library/>")

    assert manager().get_service.call_count == 2
    manager().restart.assert_not_called()


def test_nginx_installs_staticsite(settings, staticsite_path):
    from ideascube.serveradmin.catalog import Nginx, StaticSite

    p = StaticSite('w2eu', {})
    h = Nginx()
    h.install(p, staticsite_path.strpath)

    install_root = Path(settings.CATALOG_NGINX_INSTALL_DIR)

    root = install_root.join('w2eu')
    assert root.check(dir=True)

    index = root.join('index.html')
    with index.open() as f:
        assert 'static content' in f.read()


def test_nginx_removes_staticsite(settings, staticsite_path):
    from ideascube.serveradmin.catalog import Nginx, StaticSite

    p = StaticSite('w2eu', {})
    h = Nginx()
    h.install(p, staticsite_path.strpath)

    h.remove(p)

    install_root = Path(settings.CATALOG_NGINX_INSTALL_DIR)

    root = install_root.join('w2eu')
    assert root.check(exists=False)


@pytest.mark.usefixtures('db')
def test_mediacenter_installs_zippedmedia(settings, zippedmedia_path):
    from ideascube.serveradmin.catalog import MediaCenter, ZippedMedias

    assert Document.objects.count() == 0

    p = ZippedMedias('test-media', {
        'url': 'https://foo.fr/test-media.zip'})
    h = MediaCenter()
    h.install(p, zippedmedia_path.strpath)

    install_root = Path(settings.CATALOG_MEDIACENTER_INSTALL_DIR)

    root = install_root.join('test-media')
    assert root.check(dir=True)

    manifest = root.join('manifest.yml')
    assert manifest.exists()

    assert Document.objects.count() == 3
    video = Document.objects.get(title='my video')
    assert video.summary == 'my video summary'
    assert video.kind == Document.VIDEO
    assert video.lang == 'en'
    assert Document.objects.search('summary').count() == 3

    documents_tag1 = Document.objects.search(tags=['tag1'])
    documents_tag1 = set(d.title for d in documents_tag1)
    assert documents_tag1 == set(['my video', 'my doc'])

    documents_tag2 = Document.objects.search(tags=['tag2'])
    documents_tag2 = set(d.title for d in documents_tag2)
    assert documents_tag2 == set(['my video', 'my image'])

    documents_tag3 = Document.objects.search(tags=['tag3'])
    documents_tag3 = set(d.title for d in documents_tag3)
    assert documents_tag3 == set(['my video'])

    documents_tag4 = Document.objects.search(tags=['tag4'])
    documents_tag4 = set(d.title for d in documents_tag4)
    assert documents_tag4 == set(['my doc'])

    packaged_documents = Document.objects.filter(package_id='test-media')
    assert packaged_documents.count() == 3

    # Be sure that referenced documents are the ones installed by the package
    # and are not copied somewhere by the django media system.
    for document in packaged_documents:
        path = os.path.realpath(document.original.path)
        dirname = os.path.dirname(path)
        assert dirname.startswith(install_root.join('test-media').strpath)


@pytest.mark.usefixtures('db')
def test_mediacenter_removes_zippedmedia(settings, zippedmedia_path):
    from ideascube.serveradmin.catalog import MediaCenter, ZippedMedias

    p = ZippedMedias('test-media', {
        'url': 'https://foo.fr/test-media.zip'})
    h = MediaCenter()
    h.install(p, zippedmedia_path.strpath)

    assert Document.objects.count() == 3

    h.remove(p)

    assert Document.objects.count() == 0

    install_root = Path(settings.CATALOG_MEDIACENTER_INSTALL_DIR)

    root = install_root.join('test-media')
    assert root.check(exists=False)


def test_catalog_no_remote(settings):
    from ideascube.serveradmin.catalog import Catalog

    c = Catalog()
    assert c.list_remotes() == []

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).join('remotes')

    assert remotes_dir.check(dir=True)
    assert remotes_dir.listdir() == []


def test_catalog_existing_remote_json(settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).mkdir('remotes')
    remotes_dir.join('foo.json').write(json.dumps(params))

    c = Catalog()
    remotes = c.list_remotes()
    assert len(remotes) == 1

    remote = remotes[0]
    assert remote.id == params['id']
    assert remote.name == params['name']
    assert remote.url == params['url']


def test_catalog_existing_remote_yml(settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).mkdir('remotes')
    yml_file = remotes_dir.join('foo.yml')
    yml_file.write(yaml.safe_dump(params))

    c = Catalog()
    remotes = c.list_remotes()
    assert len(remotes) == 1

    remote = remotes[0]
    assert remote.id == params['id']
    assert remote.name == params['name']
    assert remote.url == params['url']

    assert yml_file.check(exists=False)
    json_data = json.loads(remotes_dir.join('foo.json').read())
    assert json_data == params


def test_catalog_add_remotes():
    from ideascube.serveradmin.catalog import Catalog, ExistingRemoteError

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

    # Try adding the same remote twice, nothing should happen
    c.add_remote('foo', 'Content by Foo', 'http://foo.fr/catalog.yml')

    # Try adding a remote with an existing id
    with pytest.raises(ExistingRemoteError) as excinfo:
        c.add_remote('foo', 'Content by Baz', 'http://baz.fr/catalog.yml')

    excinfo.match('A remote with this id already exists')

    # Try adding a remote with an existing URL
    with pytest.raises(ExistingRemoteError) as excinfo:
        c.add_remote('baz', 'Content by Baz', 'http://foo.fr/catalog.yml')

    excinfo.match('A remote with this url already exists')


def test_catalog_remove_remote_json(settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).mkdir('remotes')
    json_file = remotes_dir.join('foo.json')
    json_file.write(json.dumps(params))

    c = Catalog()
    c.remove_remote(params['id'])
    remotes = c.list_remotes()
    assert len(remotes) == 0
    assert json_file.check(exists=False)

    with pytest.raises(ValueError) as exc:
        c.remove_remote(params['id'])

    assert params['id'] in exc.exconly()


def test_catalog_remove_remote_yml(settings):
    from ideascube.serveradmin.catalog import Catalog

    params = {
        'id': 'foo', 'name': 'Content provided by Foo',
        'url': 'http://foo.fr/catalog.yml'}

    remotes_dir = Path(settings.CATALOG_STORAGE_ROOT).mkdir('remotes')
    yml_file = remotes_dir.join('foo.yml')
    yml_file.write(yaml.safe_dump(params))

    c = Catalog()
    c.remove_remote(params['id'])
    remotes = c.list_remotes()
    assert len(remotes) == 0
    assert yml_file.check(exists=False)
    assert remotes_dir.join('foo.json').check(exists=False)

    with pytest.raises(ValueError) as exc:
        c.remove_remote(params['id'])

    assert params['id'] in exc.exconly()


def test_catalog_add_package_cache(tmpdir, settings):
    from ideascube.serveradmin.catalog import Catalog

    default_cache = os.path.join(settings.CATALOG_CACHE_ROOT, 'packages')

    c = Catalog()
    assert c._package_caches == [default_cache]

    extra1 = tmpdir.mkdir('extra1').strpath
    c.add_package_cache(extra1)
    assert c._package_caches == [extra1, default_cache]

    extra2 = tmpdir.mkdir('extra2').strpath
    c.add_package_cache(extra2)
    assert c._package_caches == [extra1, extra2, default_cache]

    extra3 = tmpdir.mkdir('extra3').strpath
    c.add_package_cache(extra3)
    assert c._package_caches == [extra1, extra2, extra3, default_cache]


def test_catalog_update_cache_json(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {'foovideos': {'name': "Videos from Foo"}}}))

    c = Catalog()
    assert c._available == {}
    assert c._installed == {}

    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}

    c = Catalog()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}


def test_catalog_update_cache_yml(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.yml')
    remote_catalog_file.write(yaml.safe_dump({
        'all': {'foovideos': {'name': 'Videos from Foo'}}}))

    c = Catalog()
    assert c._available == {}
    assert c._installed == {}

    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}

    c = Catalog()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}


def test_catalog_update_cache_no_fail_if_remote_unavailable(mocker):
    from ideascube.serveradmin.catalog import Catalog
    from requests import ConnectionError

    mocker.patch('ideascube.serveradmin.catalog.urlretrieve',
                 side_effect=ConnectionError)

    c = Catalog()
    assert c._available == {}
    assert c._installed == {}

    c.add_remote(
        'foo', 'Content from Foo', 'http://example.com/not_existing')
    c.update_cache()
    assert c._available == {}
    assert c._installed == {}


def test_catalog_update_cache_updates_installed_metadata(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
           'foovideos': {
               'name': "Videos from Foo",
               'sha256sum': "abcdef",
               'type': "zipped-zim",
               'version': "1.0.0"
           }
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}
    assert c._installed == {}

    # Let's pretend we've installed stuff here
    c._installed_value = c._available.copy()
    c._persist_catalog()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}
    assert c._installed == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}

    # And now let's say that someone modified the remote metadata, for example
    # to fix an undescriptive name
    remote_catalog_file.write(json.dumps({
        'all': {
          'foovideos': {
            'name': "Awesome videos from Foo",
            'sha256sum': "abcdef",
            'type': "zipped-zim",
            'version': "1.0.0"
          }
        }
    }))

    c.update_cache()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Awesome videos from Foo'}}
    assert c._installed == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Awesome videos from Foo'}}


def test_catalog_update_cache_does_not_update_installed_metadata(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
          'foovideos': {
            'name': "Videos from Foo",
            'sha256sum': "abcdef",
            'type': "zipped-zim",
            'version': "1.0.0"
          }
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}
    assert c._installed == {}

    # Let's pretend we've installed stuff here
    c._installed_value = c._available.copy()
    c._persist_catalog()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}
    assert c._installed == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}

    # And now let's say that someone modified the remote metadata, for example
    # to fix an undescriptive name... while also publishing an update
    remote_catalog_file.write(json.dumps({
        'all': {
          'foovideos': {
            'name': "Awesome videos from Foo",
            'sha256sum': "abcdef",
            'type': "zipped-zim",
            'version': "2.0.0"
          }
        }
    }))

    c.update_cache()
    assert c._available == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '2.0.0',
        'name': 'Awesome videos from Foo'}}
    assert c._installed == {'foovideos': {
        'sha256sum': 'abcdef', 'type': 'zipped-zim', 'version': '1.0.0',
        'name': 'Videos from Foo'}}


def test_catalog_clear_metadata_cache(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all':{'foovideos':{'name': "Videos from Foo"}}}))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    assert c._available == {}
    assert c._installed == {}

    c.update_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}

    # Pretend we installed a package
    c._installed_value = {'foovideos': {}}
    downloaded_path = os.path.join(c._local_package_cache, 'foovideos')

    with open(downloaded_path, 'w') as f:
        f.write('the downloaded content')

    c.clear_metadata_cache()
    assert c._available == {}
    assert c._installed == {'foovideos': {}}
    assert os.path.exists(downloaded_path)


def test_catalog_clear_package_cache(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all':{'foovideos':{'name': "Videos from Foo"}}}))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    assert c._available == {}
    assert c._installed == {}

    c.update_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}

    # Pretend we installed a package
    c._installed_value = {'foovideos': {}}
    downloaded_path = os.path.join(c._local_package_cache, 'foovideos')

    with open(downloaded_path, 'w') as f:
        f.write('the downloaded content')

    c.clear_package_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {'foovideos': {}}
    assert not os.path.exists(downloaded_path)


def test_catalog_clear_cache(tmpdir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.mkdir('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all':{'foovideos':{'name': 'Videos from Foo'}}}))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    assert c._available == {}
    assert c._installed == {}

    c.update_cache()
    assert c._available == {'foovideos': {'name': 'Videos from Foo'}}
    assert c._installed == {}

    # Pretend we installed a package
    c._installed_value = {'foovideos': {}}
    downloaded_path = os.path.join(c._local_package_cache, 'foovideos')

    with open(downloaded_path, 'w') as f:
        f.write('the downloaded content')

    c.clear_cache()
    assert c._available == {}
    assert c._installed == {'foovideos': {}}
    assert not os.path.exists(downloaded_path)


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package(tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all':{
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_glob(
        tmpdir, sample_zim_package, settings,  mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_twice(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])
    c.install_packages(['wikipedia.tum'])


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_does_not_stop_on_failure(
        tmpdir, sample_zim_package, mocker):
    from ideascube.serveradmin.catalog import Catalog

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict(),
            'wikipedia.fr': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    def fake_install(package, download_path):
        if package.id == 'wikipedia.tum':
            raise OSError

    spy_install = mocker.patch(
        'ideascube.serveradmin.catalog.Kiwix.install',
        side_effect=fake_install)

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum', 'wikipedia.fr'])

    assert spy_install.call_count == 2
    assert 'wikipedia.tum' not in c._installed
    assert 'wikipedia.fr' in c._installed


@pytest.mark.usefixtures('db', 'systemuser')
def test_install_and_keep_the_download(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict(),
            'wikipedia.fr': dict(sample_zim_package.catalog_entry_dict(),
                                 version='2015-09'),
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    c.install_packages(['wikipedia.tum'])
    assert 'wikipedia.tum' in c._installed
    assert not (package_cache / 'wikipedia.tum-2015-08').exists()

    c.install_packages(['wikipedia.fr'], keep_downloads=True)
    assert 'wikipedia.fr' in c._installed
    assert (package_cache / 'wikipedia.fr-2015-09').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_already_downloaded(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = Path(settings.CATALOG_CACHE_ROOT)
    packagesdir = cachedir.mkdir('packages')
    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    sample_zim_package.source_path.copy(
        packagesdir.join('wikipedia.tum-2015-08'))
    sample_zim_package.source_path.remove()

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
         }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_already_in_additional_cache(
        tmpdir, sample_zim_package, settings,  mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)
    additionaldir = tmpdir.mkdir('this-could-be-a-usb-stick')

    sample_zim_package.source_path.copy(
        additionaldir.join('wikipedia.tum-2015-08'))
    sample_zim_package.source_path.remove()

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_partially_downloaded(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = Path(settings.CATALOG_CACHE_ROOT)
    packagesdir = cachedir.mkdir('packages')
    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    # Partially download the package
    packagesdir.join('wikipedia.tum-2015-08').write_binary(
        sample_zim_package.source_path.read_binary()[:100])

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_install_package_partially_downloaded_but_corrupted(
        tmpdir, sample_zim_package, settings,  mocker):
    from ideascube.serveradmin.catalog import Catalog

    cachedir = Path(settings.CATALOG_CACHE_ROOT)
    packagesdir = cachedir.mkdir('packages')
    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    # Partially download the package
    packagesdir.join('wikipedia.tum-2015-08').write_binary(
        b'corrupt download')

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


def test_catalog_install_package_does_not_exist(tmpdir, sample_zim_package):
    from ideascube.serveradmin.catalog import Catalog, NoSuchPackage

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(NoSuchPackage):
        c.install_packages(['nosuchpackage'])


def test_catalog_install_package_with_missing_type(tmpdir, sample_zim_package):
    from ideascube.serveradmin.catalog import Catalog, InvalidPackageMetadata

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    entry_dict = sample_zim_package.catalog_entry_dict()
    del(entry_dict['type'])
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': entry_dict
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(InvalidPackageMetadata):
        c.install_packages(['wikipedia.tum'])


def test_catalog_install_package_with_unknown_type(tmpdir, sample_zim_package):
    from ideascube.serveradmin.catalog import Catalog, InvalidPackageType

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': dict(sample_zim_package.catalog_entry_dict(),
                                  type='something-not-supported')
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(InvalidPackageType):
        c.install_packages(['wikipedia.tum'])


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_reinstall_package(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    zim = installdir.join('wikipedia.tum.zim')
    assert zim.check(file=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    # Now let's pretend a hacker modified the file
    good_hash = sha256(zim.read_binary())
    zim.write_text('你好嗎？', encoding='utf-8')

    # And now, reinstall
    c.reinstall_packages(['wikipedia.tum'])

    assert sha256(zim.read_binary()).hexdigest() == good_hash.hexdigest()
    assert zim.read_binary() != '你好嗎？'.encode('utf-8')


@pytest.mark.usefixtures('db', 'systemuser')
def test_reinstall_and_keep_the_download(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    c.install_packages(['wikipedia.tum'])
    assert 'wikipedia.tum' in c._installed
    assert not (package_cache / 'wikipedia.tum-2015-08').exists()

    c.reinstall_packages(['wikipedia.tum'])
    assert not (package_cache / 'wikipedia.tum-2015-08').exists()

    c.reinstall_packages(['wikipedia.tum'], keep_downloads=True)
    assert 'wikipedia.tum' in c._installed
    assert (package_cache / 'wikipedia.tum-2015-08').exists()


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_remove_package(tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_remove_package_glob(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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


def test_catalog_remove_uninstalled_package(capsys):
    from ideascube.serveradmin.catalog import Catalog

    c = Catalog()
    c.update_cache()
    assert len(c.list_installed(['*'])) == 0

    c.remove_packages(['foobar'])

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == 'foobar is not installed'


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_package(
        tmpdir, sample_zim_package, sample_zim_package_09, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata
    
    zim_file =  installdir.join('wikipedia.tum.zim')
    assert zim_file.computehash('sha256') == sample_zim_package.zim_sha256

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    c.upgrade_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    assert zim_file.computehash('sha256') == sample_zim_package_09.zim_sha256


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_package_from_old_metadata_format(
    tmpdir, sample_zim_package, sample_zim_package_09, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    installdir.join('data', 'content').ensure(dir=True)
    installed_zim_path = installdir.join('data', 'content', 'wikipedia.tum.zim')
    sample_zim_package.source_path.copy(installed_zim_path)
    # create old libary xml

    zim_library_xml = installdir.join(
        'data', 'library', 'wikipedia.tum.zim.xml')
    zim_library_xml.ensure()
    zim_library_xml.write("<library><book></book></library>");

    # Make the package installed
    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
         'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c._installed['wikipedia.tum'] = {
        'id': 'wikipedia.tum',
        'version': sample_zim_package.version,
        'type': 'zipped-zim'
    }

    # Upgrade package
    c.upgrade_packages(['wikipedia.tum'])

    assert not installed_zim_path.exists()
    assert not zim_library_xml.exists()
    assert installdir.join('wikipedia.tum.zim').check(file=True)
    assert installdir.join('wikipedia.tum.zim.json').check(file=True)

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    assert installdir.join('wikipedia.tum.zim').computehash('sha256') \
        == sample_zim_package_09.zim_sha256


@pytest.mark.usefixtures('db', 'systemuser')
def test_update_all_installed_packages(
        tmpdir, sample_zim_package, sample_zim_package_09, settings,
        testdatadir, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict(),
            'wikipedia.tumtudum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict(),
            'wikipedia.tumtudum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    c.upgrade_packages(['*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

        assert 'path="wikipedia.tumtudum.zim"' not in libdata
        assert 'indexPath="wikipedia.tumtudum.zim.idx"' not in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_uninstalled_package(
        tmpdir, sample_zim_package, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    c.upgrade_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata


@pytest.mark.usefixtures('db', 'systemuser')
def test_update_uninstalled_and_unavailable_package(tmpdir):
    from ideascube.serveradmin.catalog import Catalog, NoSuchPackage

    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({'all': {}}))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    with pytest.raises(NoSuchPackage) as excinfo:
        c.upgrade_packages(['wikipedia.tum'])

    excinfo.match('wikipedia.tum')


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_installed_but_unavailable_package(
        tmpdir, sample_zim_package, sample_zim_package_09, capsys, settings,
        mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({'all': {}}))

    c.update_cache()
    c.upgrade_packages(['wikipedia.tum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    _, err = capsys.readouterr()
    assert (
        'Ignoring package: wikipedia.tum is installed but now can not be found'
        ' in any remote') in err


@pytest.mark.usefixtures('db', 'systemuser')
def test_update_all_with_unavailable_package(
        tmpdir, sample_zim_package, sample_zim_package_09, capsys, settings,
        mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict(),
            'wikipedia.tumtudum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum', 'wikipedia.tumtudum'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

        assert 'path="wikipedia.tumtudum.zim"' in libdata
        assert 'indexPath="wikipedia.tumtudum.zim.idx"' in libdata

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    c.upgrade_packages(['*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

        assert 'path="wikipedia.tumtudum.zim"' in libdata
        assert 'indexPath="wikipedia.tumtudum.zim.idx"' in libdata

    _, err = capsys.readouterr()
    assert (
        'Ignoring package: wikipedia.tumtudum is installed but now can not be '
        'found in any remote') in err


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_package_glob(
        tmpdir, sample_zim_package, sample_zim_package_09, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata
 
    zim_file =  installdir.join('wikipedia.tum.zim')
    assert zim_file.computehash('sha256') == sample_zim_package.zim_sha256


    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    c.upgrade_packages(['wikipedia.*'])

    library = installdir.join('library.xml')
    assert library.check(exists=True)

    with library.open(mode='r') as f:
        libdata = f.read()

        assert 'path="wikipedia.tum.zim"' in libdata
        assert 'indexPath="wikipedia.tum.zim.idx"' in libdata

    assert zim_file.computehash('sha256') == sample_zim_package_09.zim_sha256

@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_update_package_already_latest(
        tmpdir, sample_zim_package, settings,mocker, capsys):
    from ideascube.serveradmin.catalog import Catalog

    installdir = Path(settings.CATALOG_KIWIX_INSTALL_DIR)
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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
    assert err.strip() == 'wikipedia.tum-2015-08 has no update available'


@pytest.mark.usefixtures('db', 'systemuser')
def test_update_and_keep_the_download(
        tmpdir, sample_zim_package, sample_zim_package_09, settings, mocker):
    from ideascube.serveradmin.catalog import Catalog

    package_cache = Path(settings.CATALOG_CACHE_ROOT) / 'packages'
    sourcedir = tmpdir.ensure('source', dir=True)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    c.install_packages(['wikipedia.tum'])
    assert not (package_cache / 'wikipedia.tum-2015-08').exists()

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    c.upgrade_packages(['wikipedia.tum'])
    assert not (package_cache / 'wikipedia.tum-2015-09').exists()

    path = sourcedir.join('wikipedia_tum_all_nopic_2015-10.zim')
    sample_zim_package_09.source_path.copy(path)

    remote_catalog_file = sourcedir.join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': dict(sample_zim_package_09.catalog_entry_dict(),
                                  version='2015-10',
                                  url='file://{}'.format(path))
        }
    }))

    c.update_cache()
    c.upgrade_packages(['wikipedia.tum'], keep_downloads=True)
    assert (package_cache / 'wikipedia.tum-2015-10').exists()


def test_catalog_list_available_packages(tmpdir):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    remote_catalog_file = tmpdir.ensure('source', dir=True).join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'foovideos': {
                'name': 'Videos from Foo',
                'type': 'zipped-zim',
                'version': '1.0.0',
                'size': '1GB'
            }
        }
    }))

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


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_list_installed_packages(tmpdir, sample_zim_package, mocker):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    remote_catalog_file = tmpdir.join('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

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
    assert pkg.version == sample_zim_package.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['wikipedia.*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['*.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_installed(['*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_list_upgradable_packages(
        tmpdir, sample_zim_package, sample_zim_package_09, mocker):
    from ideascube.serveradmin.catalog import Catalog, ZippedZim

    remote_catalog_file = tmpdir.join('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict()
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()
    c.install_packages(['wikipedia.tum'])
    assert c.list_upgradable(['*']) == []

    remote_catalog_file = tmpdir.join('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package_09.catalog_entry_dict()
        }
    }))

    c.update_cache()
    pkgs = c.list_upgradable(['nosuchpackage'])
    assert len(pkgs) == 0

    pkgs = c.list_upgradable(['wikipedia.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package_09.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['wikipedia.*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package_09.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['*.tum'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package_09.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)

    pkgs = c.list_upgradable(['*'])
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert pkg.id == 'wikipedia.tum'
    assert pkg.version == sample_zim_package_09.version
    assert pkg.size == '200KB'
    assert isinstance(pkg, ZippedZim)


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_list_upgradable_with_bad_packages(tmpdir, testdatadir):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.ensure('source', dir=True).join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'missing-metadata': {
                'size': '200KB'
            },
            'invalid-type' : {
                'type': 'unknown-type'
            }
        }
    }))

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    # Pretend we've installed some packages previously, but at some point the
    # remote was updated and...
    c._installed_value = {
        'missing-metadata': {  # ... this now misses metadata in the remote
            'type': 'static-site',
        },
        'invalid-type': {  # ... this now has an invalid type in the remote
            'type': 'zipped-medias',
        },
        'unavailable': {  # ... this got removed from the remote
            'type': 'zipped-zim',
        },
    }
    assert len(c.list_installed(['*'])) == 3

    # Ensure invalid packages are not reported as upgradable
    assert len(c.list_upgradable(['*'])) == 0


@pytest.mark.usefixtures('db', 'systemuser')
def test_catalog_list_nothandled_packages(tmpdir, sample_zim_package, mocker):
    from ideascube.serveradmin.catalog import Catalog

    remote_catalog_file = tmpdir.join('source').join('catalog.json')
    remote_catalog_file.write(json.dumps({
        'all': {
            'wikipedia.tum': sample_zim_package.catalog_entry_dict(),
            'nothandled': {
                'version': '2015-08',
                'size': '0KB',
                'url': 'file://fakeurl',
                'sha256sum': '0',
                'type': 'NOTHANDLED'
            }
        }
    }))

    mocker.patch('ideascube.serveradmin.catalog.SystemManager')

    c = Catalog()
    c.add_remote(
        'foo', 'Content from Foo',
        'file://{}'.format(remote_catalog_file.strpath))
    c.update_cache()

    pkgs = c.list_available(['*'])
    assert len(pkgs) == 1
    pkgs = c.list_nothandled(['*'])
    assert len(pkgs) == 1
    pkgs = c.list_installed(['*'])
    assert len(pkgs) == 0

    c.install_packages(['wikipedia.tum'])

    pkgs = c.list_available(['*'])
    assert len(pkgs) == 1
    pkgs = c.list_nothandled(['*'])
    assert len(pkgs) == 1
    pkgs = c.list_installed(['*'])
    assert len(pkgs) == 1


def test_catalog_doesn_t_try_to_read_file_at_instanciation(mocker):
    from ideascube.serveradmin.catalog import Catalog
    from unittest.mock import mock_open
    m = mock_open()
    mocker.patch('builtins.open', m)

    c = Catalog()
    assert not m.called

    c._available
    assert m.called


def test_catalog_update_displayed_package(systemuser):
    from ideascube.configuration import get_config, set_config
    from ideascube.serveradmin.catalog import Catalog
    set_config('home-page', 'displayed-package-ids',
               ['id1', 'id2', 'id3'], systemuser)

    Catalog._update_displayed_packages_on_home(to_remove_ids=['id1', 'id4'])
    assert get_config('home-page', 'displayed-package-ids') == ['id2', 'id3']

    Catalog._update_displayed_packages_on_home(to_add_ids=['id2', 'id4', 'id4'])
    assert get_config('home-page', 'displayed-package-ids') \
        == ['id2', 'id3', 'id4']

    Catalog._update_displayed_packages_on_home(to_remove_ids=['id2', 'id4'],
                                               to_add_ids=['id1', 'id4'])
    assert get_config('home-page', 'displayed-package-ids') \
        == ['id3', 'id1', 'id4']
