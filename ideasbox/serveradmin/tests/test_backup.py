import os
import zipfile

import pytest

from django.core.files.base import ContentFile

from ..backup import Backup

BACKUPS_ROOT = 'ideasbox/serveradmin/tests/backups'
DATA_ROOT = 'ideasbox/serveradmin/tests/data'
BACKUPED_ROOT = 'ideasbox/serveradmin/tests/backuped'


def test_backup_init_should_raise_with_malformatted_string():
    with pytest.raises(ValueError):
        Backup('xxxxx')


def test_list(monkeypatch, settings):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    settings.DATETIME_FORMAT = 'Y'
    filename = 'edoardo_0.0.0_201501231405.zip'
    good = os.path.join(BACKUPS_ROOT, filename)
    bad = os.path.join(BACKUPS_ROOT, 'donotlistme.zip')
    try:
        os.makedirs(BACKUPS_ROOT)
    except OSError:
        pass  # Already exists.
    open(good, mode='w')
    open(bad, mode='w')
    backups = list(Backup.list())
    assert len(backups) == 1
    assert backups[0].name == filename
    os.remove(good)
    os.remove(bad)
    os.rmdir(BACKUPS_ROOT)


def test_create(monkeypatch, settings):
    settings.BACKUPED_ROOT = BACKUPED_ROOT
    try:
        os.makedirs(BACKUPED_ROOT)
    except OSError:
        pass
    filename = 'edoardo_0.0.0_201501231405.zip'
    filepath = os.path.join(BACKUPS_ROOT, filename)
    try:
        # Make sure it doesn't exist before running backup.
        os.remove(filepath)
    except OSError:
        pass
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    monkeypatch.setattr('ideasbox.serveradmin.backup.make_name',
                        lambda: filename)
    proof_file = os.path.join(settings.BACKUPED_ROOT, 'backup.me')
    open(proof_file, mode='w')
    Backup.create()
    assert os.path.exists(filepath)
    assert zipfile.is_zipfile(filepath)
    archive = zipfile.ZipFile(filepath)
    print(archive.namelist())
    assert 'backup.me' in archive.namelist()
    os.remove(filepath)
    os.remove(proof_file)


def test_restore(monkeypatch, settings):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    TEST_BACKUPED_ROOT = 'ideasbox/serveradmin/tests/backuped'
    settings.BACKUPED_ROOT = TEST_BACKUPED_ROOT
    dbpath = os.path.join(TEST_BACKUPED_ROOT, 'default.sqlite')
    assert not os.path.exists(dbpath)
    backup = Backup('musasa_0.1.0_201501241620.zip')
    assert os.path.exists(backup.path)  # Should be shipped in git.
    backup.restore()
    assert os.path.exists(dbpath)
    os.remove(dbpath)


def test_load(monkeypatch):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        Backup.load(f)
    assert os.path.exists(backup_path)
    os.remove(backup_path)


def test_delete(monkeypatch):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        backup = Backup.load(f)
    assert os.path.exists(backup_path)
    backup.delete()
    assert not os.path.exists(backup_path)


def test_delete_should_not_fail_if_file_is_missing(monkeypatch):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup = Backup('doesnotexist_0.1.0_201501241620.zip')
    backup.delete()


def test_load_should_raise_if_file_is_not_a_zip():
    with pytest.raises(AssertionError):
        Backup.load(ContentFile('xxx', name='musasa_0.1.0_201501241620.zip'))


def test_exists(monkeypatch, settings):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    assert Backup.exists('musasa_0.1.0_201501241620.zip')
    assert not Backup.exists('doesnotexist.zip')
