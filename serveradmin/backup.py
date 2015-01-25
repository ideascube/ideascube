import os
import shutil
import zipfile

from datetime import datetime

from django.conf import settings


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
            raise ValueError
        self.name = name
        self.parse_name()

    def parse_name(self):
        self.source, self.version, date_ = self.basename.split('_')
        self.date = datetime.strptime(date_, Backup.DATE_FORMAT)

    @property
    def basename(self):
        return self.name[:-4]  # Minus extension.

    @property
    def path(self):
        return os.path.join(Backup.ROOT, self.name)

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
        with zipfile.ZipFile(self.path, "r") as z:
            z.extractall(settings.BACKUPED_ROOT)

    def delete(self):
        return os.remove(self.path)

    @classmethod
    def create(cls):
        name = make_name()
        backup = Backup(name)
        backup.save()
        return backup

    @classmethod
    def list(cls):
        files = os.listdir(cls.ROOT)
        files.sort()
        for name in files:
            try:
                backup = Backup(name)
            except:  # Not a regular backup file.
                continue
            yield backup

    @classmethod
    def load(cls, file_):
        assert zipfile.is_zipfile(file_)
        file_.seek(0)  # Reset cursor.
        backup = Backup(os.path.basename(file_.name))
        with open(backup.path, mode='wb') as f:
            f.write(file_.read())
        return backup
