from fnmatch import fnmatch
from glob import glob
from hashlib import sha256
from operator import attrgetter
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from django.conf import settings
from django.template.defaultfilters import filesizeformat
from lxml import etree
from progressist import ProgressBar
from resumable import DownloadCheck, DownloadError, urlretrieve
import yaml

from .systemd import Manager as SystemManager, NoSuchUnit

from ..utils import printerr


def rm(path):
    try:
        os.unlink(path)

    except IsADirectoryError:
        shutil.rmtree(path)


class InvalidFile(Exception):
    pass


class InvalidPackageMetadata(Exception):
    pass


class InvalidPackageType(Exception):
    pass


class NoSuchPackage(Exception):
    pass


class InvalidHandlerType(Exception):
    pass


class Remote:
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            d = yaml.safe_load(f.read())

            try:
                return cls(d['id'], d['name'], d['url'])

            except KeyError as e:
                raise InvalidFile(
                    'Remote file is missing a {} key: {}'.format(e, path))

    def to_file(self, path):
        with open(path, 'w') as f:
            d = {'id': self.id, 'name': self.name, 'url': self.url}
            f.write(yaml.safe_dump(d, default_flow_style=False))


class Handler:

    def __init__(self):
        default = os.path.join(settings.STORAGE_ROOT, self.name)
        setting = 'CATALOG_{}_INSTALL_DIR'.format(self.name.upper())
        self._install_dir = getattr(settings, setting, default)
        self._installed = []
        self._removed = []

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def install(self, package, download_path):
        package.install(download_path, self._install_dir)
        self._installed.append(package)

    def remove(self, package):
        package.remove(self._install_dir)
        self._removed.append(package)

    def commit(self):
        self._installed = []
        self._removed = []

    def restart_service(self, name):
        print('Restarting service', name)
        try:
            manager = SystemManager()
            service = manager.get_service(name)
        except NoSuchUnit:
            # Service is not installed, give up.
            printerr('No service named', name)
        else:
            manager.restart(service.Id)


class Kiwix(Handler):

    def commit(self):
        print('Rebuilding the Kiwix library')
        library = etree.Element('library')
        libdir = os.path.join(self._install_dir, 'data', 'library')

        for libpath in glob(os.path.join(libdir, '*.xml')):
            zimname = os.path.basename(libpath)[:-4]

            with open(libpath, 'r') as f:
                et = etree.parse(f)
                books = et.findall('book')

                # Messing with the path gets complicated otherwise
                # TODO: Can we assume this is always true for stuff distributed
                #       by kiwix?
                assert len(books) == 1

                book = books[0]
                book.set('path', 'data/content/%s' % zimname)
                book.set('indexPath', 'data/index/%s.idx' % zimname)

                library.append(book)

        with open(os.path.join(self._install_dir, 'library.xml'), 'wb') as f:
            f.write(etree.tostring(
                library, xml_declaration=True, encoding='utf-8'))

        self.restart_service('kiwix-server')
        super().commit()


class Nginx(Handler):
    template = """
server {{
    listen   80;
    server_name {server_name};
    root {root};
    index index.html;
}}
"""
    root = '/etc/nginx/'

    def commit(self):
        for pkg in self._removed:
            self.unregister_site(pkg)
        for pkg in self._installed:
            self.register_site(pkg)
        self.restart_service('nginx')
        super().commit()

    def register_site(self, package):
        available = Path(self.root, 'sites-available', package.id)
        enabled = Path(self.root, 'sites-enabled', package.id)
        server_name = '{subdomain}.{domain}'.format(subdomain=package.id,
                                                    domain=settings.DOMAIN)
        root = package.get_root_dir(self._install_dir)
        with available.open('w') as f:
            f.write(self.template.format(server_name=server_name, root=root))
        try:
            enabled.symlink_to(available)
        except FileExistsError:
            if enabled.realpath() != available.realpath():
                # Can we delete it? Even if it's not a symlink?
                # Let's prevent install for now.
                raise

    def unregister_site(self, package):
        try:
            Path(self.root, 'sites-available', package.id).unlink()
            Path(self.root, 'sites-enabled', package.id).unlink()
        except FileNotFoundError as e:
            printerr(e)


class MetaRegistry(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)

        try:
            baseclass = bases[0]
            baseclass.registered_types[cls.typename] = cls

        except IndexError:
            # This is the base class, don't register it (bases was empty)
            pass

        except AttributeError:
            # The class doesn't have a 'typename' attribute, don't register it
            pass

        return cls


class Package(metaclass=MetaRegistry):
    registered_types = {}

    def __init__(self, id, metadata):
        self.id = id
        self._metadata = metadata

    def __eq__(self, other):
        return self.id == other.id and self._metadata == other._metadata

    def __getattr__(self, name):
        try:
            return self._metadata[name]

        except KeyError:
            raise AttributeError(name)

    @property
    def version(self):
        # 0 has the advantage of always being "smaller" than any other version
        return self._metadata.get('version', '0')

    @property
    def filesize(self):
        if isinstance(self.size, int):
            return filesizeformat(self.size)
        return self.size

    def install(self, download_path, install_dir):
        raise NotImplementedError('Subclasses must implement this method')

    def remove(self, install_dir):
        raise NotImplementedError('Subclasses must implement this method')

    def assert_is_zipfile(self, path):
        if not zipfile.is_zipfile(path):
            os.unlink(path)
            raise InvalidFile('{} is not a zip file'.format(path))


class ZippedZim(Package):
    typename = 'zipped-zim'
    handler = Kiwix

    def install(self, download_path, install_dir):
        self.assert_is_zipfile(download_path)

        with zipfile.ZipFile(download_path, "r") as z:
            names = z.namelist()
            names = filter(lambda n: n.startswith('data/'), names)
            z.extractall(install_dir, members=names)

        zimname = os.path.basename(self.url).split('+', 1)[-1][:-4] + '.zim'
        datadir = os.path.join(install_dir, 'data')

        for path in glob(os.path.join(datadir, '*', '{}*'.format(zimname))):
            new = path.replace(zimname, '{0.id}.zim'.format(self))
            try:
                os.rename(path, new)
            except OSError:
                rm(new)
                os.rename(path, new)

    def remove(self, install_dir):
        zimname = '{0.id}.zim*'.format(self)
        datadir = os.path.join(install_dir, 'data')

        for path in glob(os.path.join(datadir, '*', zimname)):
            rm(path)


class StaticSite(Package):
    typename = 'static-site'
    handler = Nginx

    def get_root_dir(self, install_dir):
        return os.path.join(install_dir, self.id)

    def install(self, download_path, install_dir):
        self.assert_is_zipfile(download_path)

        with zipfile.ZipFile(download_path, "r") as z:
            z.extractall(self.get_root_dir(install_dir))

    def remove(self, install_dir):
        try:
            shutil.rmtree(self.get_root_dir(install_dir))
        except FileNotFoundError as e:
            printerr(e)


class Bar(ProgressBar):
    template = ('Download: {percent} |{animation}| {done:B}/{total:B} '
                '({speed:B}/s) | ETA: {eta}')
    done_char = '⬛'


class Catalog:
    def __init__(self):
        self._cache_base_dir = settings.CATALOG_CACHE_BASE_DIR
        os.makedirs(self._cache_base_dir, exist_ok=True)

        self._cache_remote_dir = os.path.join(self._cache_base_dir, 'remotes')
        self._load_remotes()

        self._cache_catalog = os.path.join(self._cache_base_dir, 'catalog.yml')
        self._local_package_cache = os.path.join(
            self._cache_base_dir, 'packages')

        self._load_cache()
        self._bar = Bar()

    def _progress(self, msg, i, chunk_size, remote_size):
        self._bar.update(done=(i + 1) * chunk_size, total=remote_size)

    # -- Manage packages ------------------------------------------------------
    def _get_package(self, id, source):
        try:
            metadata = source[id]

        except KeyError:
            raise NoSuchPackage(id)

        try:
            type = metadata['type']

        except KeyError:
            raise InvalidPackageMetadata('Packages must have a type')

        try:
            return Package.registered_types[type](id, metadata)

        except KeyError:
            raise InvalidPackageType(type)

    def _get_packages(self, id_patterns, source, fail_if_no_match=True):
        pkgs = []

        for id_pattern in id_patterns:
            if '*' in id_pattern:
                for id in source:
                    if fnmatch(id, id_pattern):
                        pkgs.append(self._get_package(id, source))

            else:
                try:
                    pkgs.append(self._get_package(id_pattern, source))

                except NoSuchPackage as e:
                    if fail_if_no_match:
                        raise e

        return pkgs

    def _get_handler(self, package):
        return package.handler()

    def _verify_sha256(self, path, sha256sum):
        sha = sha256()

        with open(path, 'rb') as f:
            while True:
                data = f.read(8388608)

                if not data:
                    break

                sha.update(data)

        return sha.hexdigest() == sha256sum

    def _fetch_package(self, package):
        def _progress(*args):
            self._progress(' {}'.format(package.id), *args)

        filename = '{0.id}-{0.version}'.format(package)

        for cache in self._package_caches:
            path = os.path.join(cache, filename)

            if os.path.isfile(path):
                if self._verify_sha256(path, package.sha256sum):
                    return path

                try:
                    # This might be an incomplete download, try finishing it
                    urlretrieve(
                        package.url, path, sha256sum=package.sha256sum,
                        reporthook=_progress)
                    return path

                except DownloadError as e:
                    # File was too busted, could not finish the download
                    if e.args[0] is DownloadCheck.checksum_mismatch:
                        msg = 'Downloaded file has invalid checksum'

                    else:
                        msg = 'Error downloading the file: {}'.format(e)

                    printerr(msg)
                    os.unlink(path)

        path = os.path.join(self._local_package_cache, filename)
        urlretrieve(
            package.url, path, sha256sum=package.sha256sum,
            reporthook=_progress)

        return path

    def list_installed(self, ids):
        pkgs = self._get_packages(
            ids, self._catalog['installed'], fail_if_no_match=False)
        return sorted(pkgs, key=attrgetter('id'))

    def list_available(self, ids):
        pkgs = self._get_packages(
            ids, self._catalog['available'], fail_if_no_match=False)
        return sorted(pkgs, key=attrgetter('id'))

    def list_upgradable(self, ids):
        pkgs = []

        for ipkg in self._get_packages(
                ids, self._catalog['installed'], fail_if_no_match=False):
            upkg = self._get_package(ipkg.id, self._catalog['available'])

            if ipkg != upkg:
                pkgs.append(upkg)

        return sorted(pkgs, key=attrgetter('id'))

    def install_packages(self, ids):
        used_handlers = {}
        downloaded = []

        for pkg in self._get_packages(ids, self._catalog['available']):
            if pkg.id in self._catalog['installed']:
                printerr('{0.id} is already installed'.format(pkg))
                continue

            try:
                download_path = self._fetch_package(pkg)
            except DownloadError as e:
                printerr("Failed downloading {0.id}".format(pkg))
                printerr(e)
            else:
                downloaded.append((pkg, download_path))

        for pkg, download_path in downloaded:
            handler = self._get_handler(pkg)
            print('Installing {0.id}'.format(pkg))
            try:
                handler.install(pkg, download_path)
            except Exception as e:
                printerr("Failed installing {0.id}".format(pkg))
                printerr(e)
                continue
            used_handlers[handler.__class__.__name__] = handler
            self._catalog['installed'][pkg.id] = (
                self._catalog['available'][pkg.id])
            self._persist_cache()

        for handler in used_handlers.values():
            handler.commit()

    def remove_packages(self, ids):
        used_handlers = {}

        for pkg in self._get_packages(ids, self._catalog['installed']):
            handler = self._get_handler(pkg)
            print('Removing {0.id}'.format(pkg))
            try:
                handler.remove(pkg)
            except Exception as e:
                printerr("Failed removing {0.id}".format(pkg))
                printerr(e)
                continue
            used_handlers[handler.__class__.__name__] = handler
            del(self._catalog['installed'][pkg.id])
            self._persist_cache()

        for handler in used_handlers.values():
            handler.commit()

    def upgrade_packages(self, ids):
        used_handlers = {}
        downloaded = []

        for ipkg in self._get_packages(ids, self._catalog['installed']):
            upkg = self._get_package(ipkg.id, self._catalog['available'])

            if ipkg == upkg:
                printerr('{0.id} has no update available'.format(ipkg))
                continue

            try:
                download_path = self._fetch_package(upkg)
            except DownloadError as e:
                printerr("Failed downloading {0.id}".format(upkg))
                printerr(e)
            else:
                downloaded.append((ipkg, upkg, download_path))

        for ipkg, upkg, download_path in downloaded:
            ihandler = self._get_handler(ipkg)
            uhandler = self._get_handler(upkg)
            print('Upgrading {0.id}'.format(ipkg))

            try:
                ihandler.remove(ipkg)
            except Exception as e:
                printerr("Failed removing {0.id}".format(ipkg))
                printerr(e)
                continue
            used_handlers[ihandler.__class__.__name__] = ihandler

            try:
                uhandler.install(upkg, download_path)
            except Exception as e:
                printerr("Failed installing {0.id}\n".format(upkg))
                printerr(e)
                continue
            used_handlers[uhandler.__class__.__name__] = uhandler

            self._catalog['installed'][ipkg.id] = (
                self._catalog['available'][upkg.id])
            self._persist_cache()

        for handler in used_handlers.values():
            handler.commit()

    # -- Manage local cache ---------------------------------------------------
    def _load_cache(self):
        if os.path.exists(self._cache_catalog):
            with open(self._cache_catalog, 'r') as f:
                self._catalog = yaml.safe_load(f.read())

        # yaml.safe_load returns None for an empty file.
        if not getattr(self, '_catalog', None):
            self._catalog = {'installed': {}, 'available': {}}
            self._persist_cache()

        self._package_caches = [self._local_package_cache]
        os.makedirs(self._local_package_cache, exist_ok=True)

    def _persist_cache(self):
        with open(self._cache_catalog, 'w') as f:
            f.write(yaml.safe_dump(self._catalog, default_flow_style=False))

    def add_package_cache(self, path):
        self._package_caches.append(os.path.abspath(path))

    def update_cache(self):
        self._catalog['available'] = {}

        for remote in self._remotes.values():
            # TODO: Get resumable.urlretrieve to accept a file-like object?
            fd, tmppath = tempfile.mkstemp()
            os.close(fd)

            def _progress(*args):
                self._progress(' {}'.format(remote.name), *args)

            # TODO: Verify the download with sha256sum? Crypto signature?
            urlretrieve(remote.url, tmppath, reporthook=_progress)

            with open(tmppath, 'r') as f:
                catalog = yaml.safe_load(f.read())
                # TODO: Handle content which was removed from the remote source
                self._catalog['available'].update(catalog['all'])

            os.unlink(tmppath)

        self._persist_cache()

    def clear_cache(self):
        shutil.rmtree(self._local_package_cache)
        os.mkdir(self._local_package_cache)

        self._catalog['available'] = {}
        self._persist_cache()

    # -- Manage remote sources ------------------------------------------------
    def _load_remotes(self):
        os.makedirs(self._cache_remote_dir, exist_ok=True)

        self._remotes = {}

        for path in glob(os.path.join(self._cache_remote_dir, '*.yml')):
            r = Remote.from_file(path)
            self._remotes[r.id] = r

    def list_remotes(self):
        return sorted(self._remotes.values(), key=attrgetter('id'))

    def add_remote(self, id, name, url):
        if id in self._remotes:
            raise ValueError('There already is a "{}" remote'.format(id))

        r = Remote(id, name, url)
        r.to_file(os.path.join(self._cache_remote_dir, '{}.yml'.format(id)))
        self._remotes[id] = r

    def remove_remote(self, id):
        if id not in self._remotes:
            raise ValueError('There is no "{}" remote'.format(id))

        del(self._remotes[id])
        os.unlink(os.path.join(self._cache_remote_dir, '{}.yml'.format(id)))
