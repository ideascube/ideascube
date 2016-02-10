from glob import glob
from operator import attrgetter
import os
import sys
import tempfile

from django.conf import settings
from resumable import urlretrieve
import yaml


class InvalidFile(Exception):
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


class Catalog:
    def __init__(self):
        self._cache_base_dir = settings.CATALOG_CACHE_BASE_DIR
        os.makedirs(self._cache_base_dir, exist_ok=True)

        self._cache_remote_dir = os.path.join(self._cache_base_dir, 'remotes')
        self._load_remotes()

        self._cache_catalog = os.path.join(self._cache_base_dir, 'catalog.yml')
        self._load_cache()

    def _progress(self, msg, i, chunk_size, remote_size):
        percent_done = (i + 1) * chunk_size / remote_size

        if percent_done > 1.0:
            percent_done = 1.0

        length = 79 - len(msg) - 2 - 1 - 6
        done_chars = int(percent_done * length)
        remain_chars = length - done_chars
        percent_done = int(percent_done * 1000) / 10

        p = '\r{}: {}{} {}%'.format(
            msg, "█" * done_chars, " " * remain_chars, percent_done)
        sys.stdout.write(p)

        if percent_done == 100.0:
            sys.stdout.write('\n')

        sys.stdout.flush()

    # -- Manage local cache ---------------------------------------------------
    def _load_cache(self):
        if os.path.exists(self._cache_catalog):
            with open(self._cache_catalog, 'r') as f:
                self._catalog = yaml.safe_load(f.read())

        else:
            self._catalog = {'installed': {}, 'available': {}}
            self._persist_cache()

    def _persist_cache(self):
        with open(self._cache_catalog, 'w') as f:
            f.write(yaml.safe_dump(self._catalog, default_flow_style=False))

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
