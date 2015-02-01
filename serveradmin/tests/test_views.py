import os
import zipfile

import pytest
from webtest.forms import Upload

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from ..backup import Backup
from .test_backup import BACKUPS_ROOT, DATA_ROOT

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("page", [
    ("services"),
    ("power"),
    ("backup"),
])
def test_anonymous_user_should_not_access_server(app, page):
    response = app.get(reverse("server:" + page), status=302)
    assert "login" in response["Location"]


@pytest.mark.parametrize("page", [
    ("services"),
    ("power"),
    ("backup"),
])
def test_normals_user_should_not_access_server(loggedapp, page):
    response = loggedapp.get(reverse("server:" + page), status=302)
    assert "login" in response["Location"]


def test_staff_user_should_access_services(monkeypatch, staffapp):
    class Mock(object):
        def __init__(self, *args, **kwargs):
            pass

        def communicate(self):
            return "", ""

    monkeypatch.setattr("subprocess.Popen", Mock)
    assert staffapp.get(reverse("server:services"), status=200)


def test_staff_user_should_access_power_admin(staffapp):
    assert staffapp.get(reverse("server:power"), status=200)


def test_staff_user_should_access_backup_admin(staffapp):
    assert staffapp.get(reverse("server:backup"), status=200)


def test_backup_should_list_available_backups(staffapp, backup):
    form = staffapp.get(reverse('server:backup')).forms['backup']
    radio_options = form.get('backup').options
    assert len(radio_options) == 1
    assert radio_options[0][0] == backup.name


def test_backup_button_should_save_a_new_backup(staffapp, monkeypatch,
                                                settings):
    filename = 'edoardo_0.0.0_201501231405.zip'
    filepath = os.path.join(BACKUPS_ROOT, filename)
    try:
        # Make sure it doesn't exist before running backup.
        os.remove(filepath)
    except OSError:
        pass
    monkeypatch.setattr('serveradmin.backup.Backup.ROOT', BACKUPS_ROOT)
    monkeypatch.setattr('serveradmin.backup.make_name', lambda: filename)
    proof_file = os.path.join(settings.BACKUPED_ROOT, 'backup.me')
    open(proof_file, mode='w')
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form.submit('do_create')
    assert os.path.exists(filepath)
    assert zipfile.is_zipfile(filepath)
    archive = zipfile.ZipFile(filepath)
    assert 'backup.me' in archive.namelist()
    os.remove(filepath)
    os.remove(proof_file)


def test_restore_button_should_backup_and_restore(staffapp, monkeypatch,
                                                  settings, backup):
    backups = os.listdir(DATA_ROOT)
    assert len(backups) == 1  # Only one backup exists.
    TEST_BACKUPED_ROOT = 'serveradmin/tests/backuped'
    settings.BACKUPED_ROOT = TEST_BACKUPED_ROOT
    dbpath = os.path.join(TEST_BACKUPED_ROOT, 'default.sqlite')
    assert not os.path.exists(dbpath)
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form['backup'] = backup.name
    form.submit('do_restore')
    assert os.path.exists(dbpath)
    os.remove(dbpath)
    backups = os.listdir(DATA_ROOT)
    assert len(backups) == 2
    # Remove the backup that has just been made.
    for name in backups:
        if name != backup.name:
            os.remove(os.path.join(DATA_ROOT, name))


def test_download_button_should_download_zip_file(staffapp, backup):
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form['backup'] = backup.name
    resp = form.submit('do_download')
    assert backup.name in resp['Content-Disposition']
    assert zipfile.is_zipfile(ContentFile(resp.content))


def test_delete_button_should_remote_file(staffapp, backup):
    assert len(os.listdir(DATA_ROOT)) == 1
    with open(backup.path, mode='rb') as f:
        other = Backup.load(ContentFile(f.read(),
                            name='kavumu_0.1.0_201401241620.zip'))
    assert len(os.listdir(DATA_ROOT)) == 2
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form['backup'] = other.name
    form.submit('do_delete')
    assert len(os.listdir(DATA_ROOT)) == 1


def test_upload_button_create_new_backup_with_uploaded_file(staffapp,
                                                            monkeypatch):
    monkeypatch.setattr('serveradmin.backup.Backup.ROOT', BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        form = staffapp.get(reverse('server:backup')).forms['backup']
        form['upload'] = Upload(backup_name, f.read())
        form.submit('do_upload')
        assert os.path.exists(backup_path)
        os.remove(backup_path)


def test_upload_button_do_not_create_backup_with_non_zip_file(staffapp,
                                                              monkeypatch):
    monkeypatch.setattr('serveradmin.backup.Backup.ROOT', BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form['upload'] = Upload(backup_name, 'xxx')
    resp = form.submit('do_upload')
    assert resp.status_code == 200
    assert not os.path.exists(backup_path)


def test_upload_button_do_not_create_backup_with_bad_file_name(staffapp,
                                                               monkeypatch):
    monkeypatch.setattr('serveradmin.backup.Backup.ROOT', BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        form = staffapp.get(reverse('server:backup')).forms['backup']
        form['upload'] = Upload('badname.zip', f.read())
        resp = form.submit('do_upload')
        assert resp.status_code == 200
        assert not os.path.exists(backup_path)
