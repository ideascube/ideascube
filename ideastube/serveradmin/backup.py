import os
import re
import shutil
import tarfile
import zipfile
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from ideastube import __version__


def make_name():
    """Return backup formatted file name."""
    basename = '_'.join([
        settings.IDEASTUBE_ID,
        __version__,
        datetime.now().strftime(Backup.DATE_FORMAT)
    ])
    return '{}{}'.format(basename, Backup.FORMAT_TO_EXTENSION[Backup.FORMAT])


class Backup(object):

    FORMAT = settings.BACKUP_FORMAT
    SUPPORTED_FORMATS = ('zip', 'tar', 'bztar', 'gztar')
    SUPPORTED_EXTENSIONS = ('.zip', '.tar', '.bz2', '.gz')
    FORMAT_TO_EXTENSION = dict(zip(SUPPORTED_FORMATS, SUPPORTED_EXTENSIONS))
    EXTENSION_TO_FORMAT = dict(zip(SUPPORTED_EXTENSIONS, SUPPORTED_FORMATS))
    DATE_FORMAT = "%Y%m%d%H%M"
    ROOT = os.path.join(settings.STORAGE_ROOT, 'backups')

    def __init__(self, name):
        if not name.endswith(self.SUPPORTED_EXTENSIONS):
            msg = _('backup name must end with one of {extensions}')
            raise ValueError(msg.format(extensions=self.SUPPORTED_EXTENSIONS))
        self.name = name
        self.parse_name()

    def __str__(self):
        return self.name

    def parse_name(self):
        self.source, self.version, date_ = self.basename.split('_')
        self.date = datetime.strptime(date_, Backup.DATE_FORMAT)

    @property
    def basename(self):
        # Remove every supported extension.
        return re.sub('|'.join(Backup.SUPPORTED_EXTENSIONS), '', self.name)

    @classmethod
    def make_path(cls, name):
        return os.path.join(Backup.ROOT, name)

    @property
    def path(self):
        return self.make_path(self.name)

    @property
    def size(self):
        return os.path.getsize(self.path)

    @property
    def format(self):
        return self.guess_file_format(self.name)

    def save(self):
        """Make a backup of the server data."""
        return shutil.make_archive(
            base_name=os.path.join(Backup.ROOT, self.basename),  # W/o ext.
            format=self.FORMAT,
            root_dir=settings.BACKUPED_ROOT,
            base_dir='./'
        )

    def restore(self):
        """Restore a backup from a backup name."""
        if self.format == 'zip':
            self.restore_zip()
        else:
            self.restore_tar()

    def restore_zip(self):
        with zipfile.ZipFile(self.path, "r") as z:
            z.extractall(settings.BACKUPED_ROOT)

    def restore_tar(self):
        tar = tarfile.open(self.path, mode="r", format=self.format)
        tar.extractall(settings.BACKUPED_ROOT)
        tar.close()

    @classmethod
    def guess_file_format(cls, name):
        for ext, format in cls.EXTENSION_TO_FORMAT.items():
            if name.endswith(ext):
                return format
        raise ValueError(_('Unkown format for file {}').format(name))

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
        name = os.path.basename(file_.name)
        if name.endswith('.zip'):
            if not zipfile.is_zipfile(file_):
                raise ValueError(_("Not a zip file"))
        elif not tarfile.is_tarfile(file_.name):
            raise ValueError(_("Not a tar file"))
        file_.seek(0)  # Reset cursor.
        backup = Backup(name)
        with open(backup.path, mode='wb') as f:
            f.write(file_.read())
        return backup

    @classmethod
    def exists(cls, name):
        return os.path.exists(cls.make_path(name))
