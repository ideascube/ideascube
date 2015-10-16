import os
import shutil
import zipfile
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from ideasbox import __version__


def make_name():
    """Return backup formatted file name."""
    return '{}.zip'.format('_'.join([
        settings.IDEASBOX_ID,
        __version__,
        datetime.now().strftime(Backup.DATE_FORMAT)
    ]))


class Backup(object):

    FORMAT = 'zip'
    DATE_FORMAT = "%Y%m%d%H%M"
    ROOT = os.path.join(settings.STORAGE_ROOT, 'backups')

    def __init__(self, name):
        if not name.endswith('.zip'):
            raise ValueError(_('backup name must end with .zip'))
        self.name = name
        self.parse_name()

    def __str__(self):
        return self.name

    def parse_name(self):
        self.source, self.version, date_ = self.basename.split('_')
        self.date = datetime.strptime(date_, Backup.DATE_FORMAT)

    @property
    def basename(self):
        return self.name[:-4]  # Minus extension.

    @classmethod
    def make_path(cls, name):
        return os.path.join(Backup.ROOT, name)

    @property
    def path(self):
        return self.make_path(self.name)

    @property
    def size(self):
        return os.path.getsize(self.path)

    def save(self):
        """Make a backup of the server data."""
        return shutil.make_archive(
            base_name=os.path.join(Backup.ROOT, self.basename),  # W/o .zip.
            format=self.FORMAT,
            root_dir=settings.BACKUPED_ROOT,
            base_dir='./'
        )

    def restore(self):
        """Restore a backup from a backup name."""
        with zipfile.ZipFile(self.path, "r", allowZip64=True) as z:
            z.extractall(settings.BACKUPED_ROOT)

    def delete(self):
        try:
            return os.remove(self.path)
        except OSError:
            pass

    @classmethod
    def create(cls):
        name = make_name()
        backup = Backup(name)
        backup.save()
        return backup

    @classmethod
    def list(cls):
        try:
            files = os.listdir(cls.ROOT)
        except OSError:
            # Directory does not exist yet.
            return
        files.sort()
        for name in files:
            try:
                backup = Backup(name)
            except:  # Not a regular backup file.
                continue
            yield backup

    @classmethod
    def load(cls, file_):
        assert zipfile.is_zipfile(file_), _("Not a zip file")
        file_.seek(0)  # Reset cursor.
        backup = Backup(os.path.basename(file_.name))
        with open(backup.path, mode='wb') as f:
            f.write(file_.read())
        return backup

    @classmethod
    def exists(cls, name):
        return os.path.exists(cls.make_path(name))
