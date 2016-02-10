from glob import glob
from operator import attrgetter
import os

from django.conf import settings
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
