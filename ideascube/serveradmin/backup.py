import os
import re
import shutil
import tarfile
import zipfile
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from ideascube import __version__


def make_name(format):
    """Return backup formatted file name."""
    basename = '-'.join([
        settings.IDEASCUBE_ID,
        __version__,
        datetime.now().strftime(Backup.DATE_FORMAT)
    ])
    return '{}{}'.format(basename, Backup.FORMAT_TO_EXTENSION[format])


class Backup(object):

    FORMAT = settings.BACKUP_FORMAT
    SUPPORTED_FORMATS_AT_CREATION = ('bztar', 'gztar', 'tar')
    SUPPORTED_FORMATS = ('zip', 'bztar', 'gztar', 'tar')
    SUPPORTED_EXTENSIONS = ('.zip', '.tar.bz2', '.tar.gz', '.tar')
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
        if not os.path.exists(Backup.ROOT):
            os.makedirs(Backup.ROOT)

    def __str__(self):
        return self.name

    def parse_name(self):
        try:
            self.source, self.version, date_ = self.basename.split('-')
        except ValueError:
            # Retrocompat. Remove me in 1.0.
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
        if self.format == 'zip':
            raise ValueError(_("Zip is no more supported to create backup"))

        base_name = os.path.join(Backup.ROOT, self.basename)
        base_name = "{}{}".format(base_name,
                                  self.FORMAT_TO_EXTENSION[self.format])
        try:
            mode = 'w'
            if self.format == 'gztar':
                mode = 'w:gz'
            elif self.format == 'bztar':
                mode = 'w:bz2'
            archive = tarfile.open(base_name, mode=mode)
            archive.add(settings.BACKUPED_ROOT,
                        arcname='./',
                        recursive=True,
                        exclude=os.path.islink)
        except:
            raise
        finally:
            archive.close()
        return archive

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
    def create(cls, format=None):
        format = format or Backup.FORMAT
        if format not in Backup.SUPPORTED_FORMATS_AT_CREATION:
            raise ValueError(
                _("Format {} is not supported at creation").format(format)
            )
        name = make_name(format)
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
        backup = Backup(name)
        with open(backup.path, mode='wb') as f:
           try:
               for chunk in file_.chunks():
                   f.write(chunk)
           except AttributeError:
               # file_ as no chunks,
               # read without them.
               while True:
                   content = file_.read(4096)
                   if not content:
                       break
                   f.write(content)
        if not ((name.endswith('.zip') and zipfile.is_zipfile(backup.path))
             or tarfile.is_tarfile(backup.path)
               ):
            os.unlink(backup.path)
            raise ValueError(_("Not a {} file").format(
                                 'zip' if name.endswith('.zip') else 'tar'))
        return backup

    @classmethod
    def exists(cls, name):
        return os.path.exists(cls.make_path(name))
