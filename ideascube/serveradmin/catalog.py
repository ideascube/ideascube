import shutil
from glob import glob
import zipfile
import resumable
import yaml
import requests
import os
from lxml import etree


class Catalog(object):

    APP = 'app'
    CONTENT = 'content'
    TMP_DIR = '/tmp'
    CACHE = '/tmp/catalog.yml'
    PACKAGE_CACHE = '/tmp/packages'

    def __init__(self, remote_urls, additional_cache=None):
        self.remote_urls = remote_urls
        self.package_caches = [self.PACKAGE_CACHE]

        os.makedirs(self.PACKAGE_CACHE, exist_ok=True)

    def add_remote(self, url):
        self.remote_urls.append(url)

    def add_package_cache(self, path):
        self.package_caches.append(path)

    def update(self):
        if os.path.exists(self.CACHE):
            with open(self.CACHE, 'r') as f:
                self.source = yaml.load(f.read())

        else:
            self.source = {'installed': {}, 'current': {}}

        for url in self.remote_urls:
            with open(url) as f:
                catalog = yaml.load(f.read())
                self.source['current'].update(catalog['current'])

        self._persist_cache()

    def fetch_package(self, package):
        for cache in self.package_caches:
            path = os.path.join(cache, package.filename)

            if os.path.exists(path):
                return path

        path = os.path.join(self.PACKAGE_CACHE, package.filename)
        resumable.urlretrieve(package.url, path) # TODO: sha256sum
        return path

    def get_installed(self, id):
        return Content(id, self.source['installed'][id], self)

    def get_available(self, id):
        return Content(id, self.source['current'][id], self)

    def empty_cache(self):
        shutil.rmtree(self.PACKAGE_CACHE)
        os.mkdir(self.PACKAGE_CACHE)

    def _persist_cache(self):
        with open(self.CACHE, 'w') as f:
            f.write(yaml.dump(self.source))

    def list_installed(self, *args):
        print(', '.join(self.source['installed']))

    def list_available(self, *args):
        print(', '.join(self.source['current']))

    def install(self, ids):
        app = Kiwix()

        for id in ids:
            package = self.get_available(id)

            if package.installed:
                print("{} is already installed".format(id))
                continue

            app.install(package)
            self.source['installed'][id] = package.metadata

        app.commit()
        self._persist_cache()

    def remove(self, ids):
        app = Kiwix()

        for id in ids:
            package = self.get_installed(id)
            app.remove(package)
            del(self.source['installed'][id])

        app.commit()
        self._persist_cache()

    def upgrade(self, ids=None):
        if ids is None:
            # Update all
            ids = [p['id'] for p in self.source['installed']]

        app = Kiwix()

        for id in ids:
            package = self.get_available(id)

            if not package.installed:
                print('{} is not installed, ignoring'.format(id))
                continue

            if self.source['current'][id] == self.source['installed'][id]:
                print('{} has no update available, ignoring'.format(id))
                continue

            app.update(package)
            self.source['installed'][id] = package.metadata

        app.commit()
        self._persist_cache()


class Content(object):

    def __init__(self, id, metadata, catalog):
        self.id = id
        self.metadata = metadata
        self.catalog = catalog
        self.__dict__.update(metadata)

    @property
    def filename(self):
        return '{}-{}'.format(self.id, self.metadata.get('version', 'noversion'))

    @property
    def installed(self):
        return self.id in self.catalog.source['installed']

    def install(self, app):
        download_path = self.catalog.fetch_package(self)

        if not zipfile.is_zipfile(download_path):
            os.unlink(download_path)
            raise ValueError('{} is not a zip file, file has been deleted'.format(download_path))

        with zipfile.ZipFile(download_path, "r") as z:
            names = z.namelist()
            names = filter(lambda n: n.startswith('data/'), names)
            z.extractall(app.DIR, members=names)

        zipname = os.path.basename(self.url)
        zimname = zipname.split('+', 1)[-1]
        zimname = zimname[:-4] + '.zim'

        for zim in glob(os.path.join(app.DIR, 'data', '*', '%s*' % zimname)):
            new = zim.replace(zimname, self.id + '.zim')
            os.rename(zim, new)

    def remove(self, app):
        zimname = '%s.zim' % self.id

        for path in glob(os.path.join(app.DIR, 'data', '*', '%s*' % zimname)):
            try:
                os.unlink(path)

            except IsADirectoryError:
                shutil.rmtree(path)


class Kiwix(object):

    DIR = '/tmp/kiwix'
    LIBRARY = '/tmp/kiwix/library.xml'

    def commit(self):
        self._update_library()

    def _update_library(self):
        library = etree.Element('library')
        libdir = os.path.join(self.DIR, 'data', 'library')

        for l in os.listdir(libdir):
             zimname = os.path.splitext(l)[0]
             l = os.path.join(libdir, l)

             with open(l, 'r') as f:
                 et = etree.parse(f)
                 books = et.findall('book')

                 # Messing with the path gets complicated otherwise
                 # TODO: Can we assume this is always true for stuff coming from kiwix?
                 assert len(books) == 1

                 book = books[0]
                 book.set('path', 'data/content/%s' % zimname)
                 book.set('indexPath', 'data/content/%s.idx' % zimname)

                 library.append(book)

        with open(self.LIBRARY, 'wb') as f:
            f.write(etree.tostring(library, xml_declaration=True, pretty_print=True, encoding='utf-8'))

    def install(self, package):
        package.install(self)

    def remove(self, package):
        package.remove(self)

    def update(self, package):
        package.remove(self)
        package.install(self)


import sys
catalog = Catalog(['./ideascube/serveradmin/tests/data/catalog.yml'])
catalog.update()

action = sys.argv[1]
packageids = sys.argv[2:]

print("%s-ing %s" % (action, packageids))
getattr(catalog, action)(packageids)
