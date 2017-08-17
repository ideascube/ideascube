from django.contrib.staticfiles.storage import StaticFilesStorage

from . import __version__ as ideascube_version


class VersionedStaticFilesStorage(StaticFilesStorage):
    def url(self, name):
        url = super().url(name)
        url += '?version={ideascube_version}'.format(ideascube_version=ideascube_version)

        return url
