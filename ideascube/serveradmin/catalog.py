from datetime import timedelta
from fnmatch import fnmatch
from glob import glob
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
from requests import ConnectionError
import yaml

from ideascube.configuration import get_config, set_config
from ideascube.mediacenter.forms import PackagedDocumentForm
from ideascube.mediacenter.models import Document
from ideascube.mediacenter.utils import guess_kind_from_filename
from ideascube.models import User
from ideascube.templatetags.ideascube_tags import smart_truncate
from ideascube.utils import (
    MetaRegistry, classproperty, get_file_sha256, printerr, rm, urlretrieve,
)

from .systemd import Manager as SystemManager, NoSuchUnit


def load_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f.read())


def persist_to_file(path, data):
    """Save catalog data to a local file

    Note: The function assumes that the data is serializable.
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(yaml.safe_dump(data, default_flow_style=False))


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


class InvalidPackageContent(Exception):
    pass


class ExistingRemoteError(Exception):
    def __init__(self, remote):
        self.remote = remote

    def __str__(self):
        return "Remote {} already exists".format(self.remote.id)


class Remote:
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url

    @classmethod
    def from_file(cls, path):
        d = load_from_file(path)

        try:
            return cls(d['id'], d['name'], d['url'])

        except KeyError as e:
            raise InvalidFile(
                'Remote file is missing a {} key: {}'.format(e, path))

    def to_file(self, path):
        d = {'id': self.id, 'name': self.name, 'url': self.url}
        persist_to_file(path, d)


class Handler:
    @classproperty
    @classmethod
    def _install_dir(cls):
        name = cls.__name__.lower()
        default = os.path.join(settings.STORAGE_ROOT, name)
        setting = 'CATALOG_{}_INSTALL_DIR'.format(name.upper())

        return getattr(settings, setting, default)

    @classmethod
    def install(cls, package, download_path):
        package.install(download_path, cls._install_dir)

    @classmethod
    def remove(cls, package):
        package.remove(cls._install_dir)

    @classmethod
    def commit(cls):
        pass

    @classmethod
    def restart_service(cls, name):
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
    @classmethod
    def commit(cls):
        print('Rebuilding the Kiwix library')
        library = etree.Element('library')
        libdir = os.path.join(cls._install_dir, 'data', 'library')
        os.makedirs(libdir, exist_ok=True)

        for libpath in glob(os.path.join(libdir, '*.xml')):
            zimname = os.path.basename(libpath)[:-4]

            with open(libpath, 'r') as f:
                et = etree.parse(f)
                books = et.findall('book')

                # We only want to handle a single zim per zip
                assert len(books) == 1

                book = books[0]
                book.set('path', 'data/content/%s' % zimname)

                index_path = 'data/index/%s.idx' % zimname
                if os.path.isdir(os.path.join(cls._install_dir, index_path)):
                    book.set('indexPath', index_path)

                library.append(book)

        with open(os.path.join(cls._install_dir, 'library.xml'), 'wb') as f:
            f.write(etree.tostring(
                library, xml_declaration=True, encoding='utf-8'))

        cls.restart_service('kiwix-server')
        super().commit()


class Nginx(Handler):
    @classmethod
    def commit(cls):
        cls.restart_service('nginx')
        super().commit()


class MediaCenter(Handler):
    pass


class Package(metaclass=MetaRegistry):
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
        try:
            return filesizeformat(int(self.size))
        except ValueError:
            return self.size

    def install(self, download_path, install_dir):
        raise NotImplementedError('Subclasses must implement this method')

    def remove(self, install_dir):
        raise NotImplementedError('Subclasses must implement this method')

    def assert_is_zipfile(self, path):
        if not zipfile.is_zipfile(path):
            rm(path)
            raise InvalidFile('{} is not a zip file'.format(path))


class ZippedZim(Package, typename='zipped-zim'):
    handler = Kiwix
    template_id = "kiwix"

    def install(self, download_path, install_dir):
        self.assert_is_zipfile(download_path)

        with zipfile.ZipFile(download_path, "r") as z:
            names = z.namelist()
            names = filter(lambda n: n.startswith('data/'), names)
            # Make it a list so we can reuse it later
            names = list(names)
            z.extractall(install_dir, members=names)

        datadir = os.path.join(install_dir, 'data')

        for path in glob(os.path.join(datadir, '*', '*.zim*')):
            relpath = os.path.relpath(path, install_dir)

            if os.path.isdir(path):
                # Dirs end with a / in the zip file list
                relpath += '/'

            if relpath not in names:
                # Ignore zim files installed by other packages
                continue

            zimname = os.path.basename(path).split('.zim')[0] + '.zim'
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

    # [FIXME] Thoses two properties look like hacks.
    # We may want to find a way to find those information in the package or
    # catalog metadata.
    # For now, use special cases.
    @property
    def theme(self):
        # Strings "discover", "read" and "learn" must be marked as translatable.
        # For this we use a dummy function who do nothing.
        # As the function is named _, gettext will mark the strings.
        _ = lambda t: t
        base_name, extension = self.id.rsplit('.', 1)
        if base_name in ("wikipedia", "wikivoyage", "vikidia"):
            return _("discover")
        if base_name in ("gutemberg", "icd10", "wikisource", "wikibooks", "bouquineux"):
            return _("read")
        return _("learn")

    @property
    def css_class(self):
        base_name, _ = self.id.rsplit('.', 1)
        if base_name.startswith('ted'):
            return 'ted'
        return base_name


class SimpleZipPackage(Package, no_register=True):
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


class StaticSite(SimpleZipPackage, typename='static-site'):
    template_id = 'static-site'
    handler = Nginx

    # [FIXME] This propertie looks like hacks.
    @property
    def theme(self):
        # theme string must be marked as translatable.
        # For this we use a dummy function who do nothing.
        # As the function is named _, gettext will mark the strings.
        _ = lambda t: t
        if '.map' in self.id or self.id in ['maguare.es', 'cinescuela.es']:
            return _('discover')
        return _('info')

    @property
    def css_class(self):
        if '.map' in self.id:
            return 'maps'
        base_name, *_ = self.id.split('.')
        return base_name


class ZippedMedias(SimpleZipPackage, typename='zipped-medias'):
    handler = MediaCenter
    template_id = "media-package"

    def remove(self, install_dir):
        # Easy part here. Just delete documents from the package.
        Document.objects.filter(package_id=self.id).delete()
        super().remove(install_dir)

    def install(self, download_path, install_dir):
        super().install(download_path, install_dir)
        print('Adding medias to mediacenter database.')
        root = self.get_root_dir(install_dir)
        manifestfile = Path(root, 'manifest.yml')

        try:
            with manifestfile.open('r') as m:
                manifest = yaml.safe_load(m.read())

        except FileNotFoundError:
            raise InvalidPackageContent('Missing manifest file in {}'.format(
                self.id))

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        catalog_path = os.path.join(settings.MEDIA_ROOT, "catalog")
        try:
            os.symlink(install_dir, catalog_path)
        except FileExistsError:
            if not os.path.islink(catalog_path):
                printerr("Cannot install package {}. {} must not exist "
                         "or being a symlink.".format(self.id, catalog_path))
                return

        pseudo_install_dir = os.path.join(catalog_path, self.id)
        for media in manifest['medias']:
            try:
                self._install_media(media, pseudo_install_dir)
            except Exception as e:
                # This can lead to installed package with uninstall media.
                # We sould handle this somehow.
                printerr("Cannot install media {} from package {} : {}".format(
                    media['title'], self.id, e))
                continue

    def _install_media(self, media_info, pseudo_install_dir):
        try:
            media_info['title'] = smart_truncate(media_info['title'].strip())
        except KeyError:
            raise InvalidPackageContent('Missing title in {}'.format(
                media_info))

        lang = media_info.get('lang', '').strip().lower()

        if not lang:
            # Unsure if we shouldn't use `get_language()` instead of
            # LANGUAGE_CODE from the settings.
            media_info['lang'] = settings.LANGUAGE_CODE

        kind = media_info.get('kind', '').strip().lower()
        if not kind or not hasattr(Document, kind.upper()):
            kind = guess_kind_from_filename(media_info['path'])
            media_info['kind'] = kind or Document.OTHER

        media_info['package_id'] = self.id
        media_info['original'] = os.path.join(pseudo_install_dir,
                                              media_info['path'])

        if media_info.get('preview'):
            media_info['preview'] = os.path.join(pseudo_install_dir,
                                                 media_info['preview'])

        self._save_media(media_info, pseudo_install_dir)

    def _save_media(self, metadata, install_dir):
        form = PackagedDocumentForm(path=install_dir,
                                   data=metadata,
                                   instance=None)

        if form.is_valid():
            form.save()
        else:
            lerr = ["Some values are not valid :"]
            for field, error in form.errors.items():
                lerr.append(" - {}: {}".format(field, error.as_text()))
            raise InvalidPackageContent("\n".join(lerr))


class Bar(ProgressBar):
    template = ('Download: {percent} |{animation}| {done:B}/{total:B} '
                '({speed:B}/s) | ETA: {eta}')
    throttle = timedelta(seconds=1)


class Catalog:
    def __init__(self):
        self._cache_root = settings.CATALOG_CACHE_ROOT
        os.makedirs(self._cache_root, exist_ok=True)

        self._catalog_cache = os.path.join(self._cache_root, 'catalog.yml')
        self._local_package_cache = os.path.join(self._cache_root, 'packages')
        os.makedirs(self._local_package_cache, exist_ok=True)

        self._storage_root = settings.CATALOG_STORAGE_ROOT
        os.makedirs(self._storage_root, exist_ok=True)

        self._installed_storage = os.path.join(
            self._storage_root, 'installed.yml')
        self._remote_storage = os.path.join(self._storage_root, 'remotes')
        os.makedirs(self._remote_storage, exist_ok=True)

        self._remotes_value = None
        self._available_value = None
        self._installed_value = None
        self._package_caches = [self._local_package_cache]

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

    def _get_package_ids(self, id_patterns, source):
        for id_pattern in id_patterns:
            if '*' in id_pattern:
                for pkg_id in source:
                    if fnmatch(pkg_id, id_pattern):
                        yield pkg_id

            else:
                yield id_pattern

    def _verify_sha256(self, path, sha256sum):
        sha = get_file_sha256(path)
        return sha == sha256sum

    def _fetch_package(self, package):
        def _progress(*args):
            self._progress(' {}'.format(package.id), *args)

        filename = '{0.id}-{0.version}'.format(package)

        for cache in self._package_caches:
            path = os.path.join(cache, filename)

            if os.path.isfile(path):
                if self._verify_sha256(path, package.sha256sum):
                    return path

                # This might be an incomplete download, try finishing it
                try:
                    urlretrieve(
                        package.url, path, sha256sum=package.sha256sum,
                        reporthook=_progress)

                except Exception as e:
                    printerr(e)

        path = os.path.join(self._local_package_cache, filename)
        urlretrieve(
            package.url, path, sha256sum=package.sha256sum,
            reporthook=_progress)

        return path

    def list_installed(self, ids):
        ids = self._get_package_ids(ids, self._installed)
        pkgs = []

        for pkg_id in ids:
            try:
                pkgs.append(self._get_package(pkg_id, self._installed))

            except (InvalidPackageMetadata, InvalidPackageType, NoSuchPackage):
                continue

        return sorted(pkgs, key=attrgetter('id'))

    def list_available(self, ids):
        ids = self._get_package_ids(ids, self._available)
        pkgs = []

        for pkg_id in ids:
            try:
                pkgs.append(self._get_package(pkg_id, self._available))

            except (InvalidPackageMetadata, InvalidPackageType, NoSuchPackage):
                continue

        return sorted(pkgs, key=attrgetter('id'))

    def list_upgradable(self, ids):
        ids = self._get_package_ids(ids, self._installed)
        pkgs = []

        for pkg_id in ids:
            try:
                ipkg = self._get_package(pkg_id, self._installed)

            except (InvalidPackageMetadata, InvalidPackageType, NoSuchPackage):
                continue

            upkg = self._get_package(ipkg.id, self._available)

            if ipkg != upkg:
                pkgs.append(upkg)

        return sorted(pkgs, key=attrgetter('id'))

    def list_nothandled(self, ids):
        pkgs = []
        source = dict(self._available)
        source.update(self._installed)
        for pkgid, metadata in source.items():
            try:
                self._get_package(pkgid, source)
            except InvalidPackageType:
                pkgs.append(Package(pkgid, metadata))

        return sorted(pkgs, key=attrgetter('id'))

    @staticmethod
    def _update_displayed_packages_on_home(*, to_remove_ids=None, to_add_ids=None):
        displayed_packages = get_config('home-page', 'displayed-package-ids')
        if to_remove_ids:
            displayed_packages = [id for id in displayed_packages if id not in to_remove_ids]
        if to_add_ids:
            displayed_packages.extend(id for id in to_add_ids if id not in displayed_packages)
        set_config('home-page', 'displayed-package-ids',
                   displayed_packages, User.objects.get_system_user())

    def install_packages(self, ids):
        ids = self._get_package_ids(ids, self._available)
        used_handlers = {}
        downloaded = []
        installed_ids = []

        for pkg_id in ids:
            pkg = self._get_package(pkg_id, self._available)

            if pkg.id in self._installed:
                printerr('{0.id} is already installed'.format(pkg))
                continue

            try:
                download_path = self._fetch_package(pkg)
                downloaded.append((pkg, download_path))

            except Exception as e:
                printerr(e)

        for pkg, download_path in downloaded:
            handler = pkg.handler
            print('Installing {0.id}'.format(pkg))
            try:
                handler.install(pkg, download_path)
            except Exception as e:
                printerr("Failed installing {0.id}".format(pkg))
                printerr(e)
                continue
            used_handlers[handler.__class__.__name__] = handler
            self._installed[pkg.id] = self._available[pkg.id].copy()
            installed_ids.append(pkg.id)
            self._persist_catalog()

        self._update_displayed_packages_on_home(to_add_ids=installed_ids)

        for handler in used_handlers.values():
            handler.commit()

    def remove_packages(self, ids, commit=True):
        ids = self._get_package_ids(ids, self._available)
        used_handlers = {}

        for pkg_id in ids:
            pkg = self._get_package(pkg_id, self._installed)
            handler = pkg.handler
            print('Removing {0.id}'.format(pkg))
            try:
                handler.remove(pkg)
            except Exception as e:
                printerr("Failed removing {0.id}".format(pkg))
                printerr(e)
                continue
            used_handlers[handler.__class__.__name__] = handler
            del(self._installed[pkg.id])
            self._persist_catalog()

        self._update_displayed_packages_on_home(to_remove_ids=ids)

        if not commit:
            return

        for handler in used_handlers.values():
            handler.commit()

    def reinstall_packages(self, ids):
        self.remove_packages(ids, commit=False)
        self.install_packages(ids)

    def upgrade_packages(self, ids):
        ids = self._get_package_ids(ids, self._available)
        used_handlers = {}
        downloaded = []

        for pkg_id in ids:
            ipkg = self._get_package(pkg_id, self._installed)
            upkg = self._get_package(ipkg.id, self._available)

            if ipkg == upkg:
                printerr('{0.id} has no update available'.format(ipkg))
                continue

            try:
                download_path = self._fetch_package(upkg)
                downloaded.append((ipkg, upkg, download_path))

            except Exception as e:
                printerr(e)

        for ipkg, upkg, download_path in downloaded:
            ihandler = ipkg.handler
            uhandler = upkg.handler
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

            self._installed[ipkg.id] = self._available[upkg.id].copy()
            self._persist_catalog()

        for handler in used_handlers.values():
            handler.commit()

    # -- Manage local cache ---------------------------------------------------
    @property
    def _available(self):
        if self._available_value is None:
            self._available_value = {}
            try:
                catalog = load_from_file(self._catalog_cache)

            except FileNotFoundError:
                # That's ok.
                pass

            else:
                # load_from_file returns None for empty files
                if catalog is not None:
                    if 'available' in catalog and 'installed' in catalog:
                        # The cache on file is in the old format
                        # https://framagit.org/ideascube/ideascube/issues/376
                        self._available_value = catalog['available']
                        self._installed_value = catalog['installed']

                    else:
                        self._available_value = catalog
        return self._available_value

    @property
    def _installed(self):
        if self._installed_value is None:
            self._installed_value = {}

            try:
                installed = load_from_file(self._installed_storage)

            except FileNotFoundError:
                # Try compatible old format
                try:
                    catalog = load_from_file(self._catalog_cache)
                except FileNotFoundError:
                    # That's ok
                    pass

                else:
                    # load_from_file returns None for empty files
                    if catalog is not None:
                        if 'available' in catalog and 'installed' in catalog:
                            # The cache on file is in the old format
                            # https://framagit.org/ideascube/ideascube/issues/376
                            self._available_value = catalog['available']
                            self._installed_value = catalog['installed']
                        elif self._available_value is None:
                            # Now we have load the catalog, let's save it.
                            self._available_value = catalog

            else:
                # load_from_file returns None for empty files
                if installed is not None:
                    self._installed_value = installed

        return self._installed_value

    def _persist_catalog(self):
        persist_to_file(self._catalog_cache, self._available)
        persist_to_file(self._installed_storage, self._installed)

    def _update_installed_metadata(self):
        # These are the keys we must only ever update with an actual package
        # upgrade, and thus not here.
        blacklist = (
            'sha256sum',
            'type',
            'version',
        )

        for pkgid in self._installed:
            installed = self._installed[pkgid]
            available = self._available.get(pkgid)

            if available is None:
                # The package was installed but it isn't available any more
                continue

            if any(installed[k] != available[k] for k in blacklist):
                # We really should upgrade this package, not update its
                # installed metadata here
                continue

            # The remote catalog metadata for this package changed, but the
            # values associated to blacklisted keys didn't. It is thus the
            # exact same package, just with updated (and let's hope improved)
            # name, description, ...
            self._installed[pkgid] = available.copy()

    def add_package_cache(self, path):
        self._package_caches.append(os.path.abspath(path))

    def update_cache(self):
        self._available_value = {}

        for remote in self._remotes.values():
            # TODO: Get resumable.urlretrieve to accept a file-like object?
            with tempfile.NamedTemporaryFile() as fd:
                tmppath = fd.name

                def _progress(*args):
                    self._progress(' {}'.format(remote.name), *args)

                # TODO: Verify the download with sha256sum? Crypto signature?
                try:
                    urlretrieve(remote.url, tmppath, reporthook=_progress)

                except ConnectionError:
                    print("Warning: Impossible to connect to the remote "
                          "{remote.name}({remote.url}).\n"
                          "Continuing without it.".format(remote=remote))
                    continue

                catalog = load_from_file(tmppath)

                # TODO: Handle content which was removed from the remote source
                self._available.update(catalog['all'])

        self._update_installed_metadata()
        self._persist_catalog()

    def clear_cache(self):
        rm(self._local_package_cache)
        os.mkdir(self._local_package_cache)

        self._available_value = {}
        self._persist_catalog()

    # -- Manage remote sources ------------------------------------------------
    @property
    def _remotes(self):
        if self._remotes_value is None:
            self._load_remotes()
        return self._remotes_value

    def _load_remotes(self):
        self._remotes_value = {}

        for path in glob(os.path.join(self._remote_storage, '*.yml')):
            r = Remote.from_file(path)
            self._remotes_value[r.id] = r

        if self._remotes_value:
            return

        # We might have remotes in the old location
        old_remote_cache = os.path.join(self._cache_root, 'remotes')

        for path in glob(os.path.join(old_remote_cache, '*.yml')):
            r = Remote.from_file(path)
            self.add_remote(r.id, r.name, r.url)

        if self._remotes_value:
            # So we did have old remotes after all...
            rm(old_remote_cache)

    def list_remotes(self):
        return sorted(self._remotes.values(), key=attrgetter('id'))

    def add_remote(self, id, name, url):
        remote = self._remotes.get(id)
        if remote:
            raise ExistingRemoteError(remote)

        remote = Remote(id, name, url)
        remote.to_file(os.path.join(self._remote_storage,
                       '{}.yml'.format(id)))
        self._remotes[id] = remote

    def remove_remote(self, id):
        if id not in self._remotes:
            raise ValueError('There is no "{}" remote'.format(id))

        del(self._remotes[id])
        rm(os.path.join(self._remote_storage, '{}.yml'.format(id)))
