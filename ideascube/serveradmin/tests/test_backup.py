import os
import tarfile

import pytest

from django.core.files.base import ContentFile

from ..backup import Backup

BACKUPS_ROOT = 'ideascube/serveradmin/tests/backups'
DATA_ROOT = 'ideascube/serveradmin/tests/data/backup'


def test_backup_init_should_raise_with_malformatted_string():
    with pytest.raises(ValueError):
        Backup('xxxxx')


def test_underscore_as_separator_should_still_be_supported():
    Backup('edoardo-0.0.0-201501231405.tar.gz')


@pytest.mark.parametrize('input,expected', [
    ('name.zip', 'zip'),
    ('name.tar', 'tar'),
    ('name.tar.bz2', 'bztar'),
    ('name.tar.gz', 'gztar'),
])
def test_guess_format_from_name(input, expected):
    assert Backup.guess_file_format(input) == expected


def test_guess_format_from_name_fails():
    with pytest.raises(ValueError):
        Backup.guess_file_format('name.png')


@pytest.mark.usefixtures('backup_root')
def test_list(monkeypatch, settings):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    settings.DATETIME_FORMAT = 'Y'
    filename = 'edoardo-0.0.0-201501231405.tar'
    good = os.path.join(BACKUPS_ROOT, filename)
    bad = os.path.join(BACKUPS_ROOT, 'donotlistme.tar')
    open(good, mode='w')
    open(bad, mode='w')
    backups = list(Backup.list())
    assert len(backups) == 1
    assert backups[0].name == filename
    assert str(backups[0]) == filename
    os.remove(good)
    os.remove(bad)


@pytest.mark.parametrize('format,extension', [
    ('tar', '.tar'),
    ('bztar', '.tar.bz2'),
    ('gztar', '.tar.gz'),
])
@pytest.mark.usefixtures('backup_root')
def test_create_tarfile(monkeypatch, settings, format, extension):
    filename = 'edoardo-0.0.0-201501231405' + extension
    filepath = os.path.join(BACKUPS_ROOT, filename)
    try:
        # Make sure it doesn't exist before running backup.
        os.remove(filepath)
    except OSError:
        pass
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.FORMAT', format)
    monkeypatch.setattr('ideascube.serveradmin.backup.make_name',
                        lambda f: filename)
    proof_file = os.path.join(settings.BACKUPED_ROOT, 'backup.me')
    open(proof_file, mode='w')
    symlink_file = os.path.join(settings.BACKUPED_ROOT, 'symlink')
    os.symlink('backup.me', symlink_file)
    Backup.create()
    assert os.path.exists(filepath)
    assert tarfile.is_tarfile(filepath)
    archive = tarfile.open(filepath)
    assert './backup.me' in archive.getnames()
    assert './symlink' not in archive.getnames()
    archive.close()
    os.remove(filepath)
    os.remove(proof_file)
    os.remove(symlink_file)


def test_create_zipfile_must_fail(monkeypatch, tmpdir):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT', str(tmpdir))
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.FORMAT', 'zip')
    assert len(list(Backup.list())) == 0
    with pytest.raises(ValueError):
        Backup.create()
    assert len(list(Backup.list())) == 0


@pytest.mark.parametrize('extension', [
    ('.zip'),
    ('.tar'),
    ('.tar.gz'),
    ('.tar.bz2'),
])
def test_restore(monkeypatch, settings, extension):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    dbpath = os.path.join(settings.BACKUPED_ROOT, 'default.sqlite')
    assert not os.path.exists(dbpath)
    backup = Backup('musasa-0.1.0-201501241620' + extension)
    assert os.path.exists(backup.path)  # Should be shipped in git.
    backup.restore()
    assert os.path.exists(dbpath)
    os.remove(dbpath)


@pytest.mark.parametrize('extension', [
    ('.zip'),
    ('.tar'),
    ('.tar.gz'),
    ('.tar.bz2'),
])
@pytest.mark.usefixtures('backup_root')
def test_load(monkeypatch, extension):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup_name = 'musasa-0.1.0-201501241620' + extension
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        Backup.load(f)
    assert os.path.exists(backup_path)
    os.remove(backup_path)


@pytest.mark.parametrize('extension', [
    ('.zip'),
    ('.tar'),
    ('.tar.gz'),
    ('.tar.bz2'),
])
@pytest.mark.usefixtures('backup_root')
def test_delete(monkeypatch, extension):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup_name = 'musasa-0.1.0-201501241620' + extension
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        backup = Backup.load(f)
    assert os.path.exists(backup_path)
    backup.delete()
    assert not os.path.exists(backup_path)


@pytest.mark.usefixtures('backup_root')
def test_delete_should_not_fail_if_file_is_missing(monkeypatch):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup = Backup('doesnotexist-0.1.0-201501241620.tar')
    backup.delete()


def test_load_should_raise_if_file_is_not_a_zip():
    with pytest.raises(ValueError) as excinfo:
        Backup.load(ContentFile(b'xxx', name='musasa_0.1.0_201501241620.zip'))
        assert 'Not a zip file' in str(excinfo.value)


@pytest.mark.usefixtures('backup_root')
def test_load_should_raise_if_file_is_not_a_tar():
    bad_file = os.path.join(BACKUPS_ROOT, 'musasa_0.1.0_201501241620.tar')
    with pytest.raises(ValueError) as excinfo:
        with open(bad_file, 'w') as f:
            Backup.load(f)
            assert 'Not a tar file' in str(excinfo.value)
    os.remove(bad_file)


def test_exists(monkeypatch):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    assert Backup.exists('musasa-0.1.0-201501241620.tar')
    assert not Backup.exists('doesnotexist.tar')
