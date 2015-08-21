import os
import zipfile

import pytest
from webtest.forms import Upload
from mock import MagicMock, patch

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from ..backup import Backup
from .test_backup import BACKUPS_ROOT, DATA_ROOT

from wifi import Cell, Scheme
from wifi.exceptions import ConnectionError
from ..views import interface
from django.utils.translation import ugettext as _
from .conftest import getproperty, setproperties, set_hotspots
import subprocess

pytestmark = pytest.mark.django_db


class FakePopen(object):
    def __init__(self, *args, **kwargs):
        self.returncode = 0

    def communicate(self):
        return "", ""

    def wait(self):
        pass


@pytest.mark.parametrize("page", [
    ("services"),
    ("power"),
    ("backup"),
    ("battery"),
])
def test_anonymous_user_should_not_access_server(app, page):
    response = app.get(reverse("server:" + page), status=302)
    assert "login" in response["Location"]


@pytest.mark.parametrize("page", [
    ("services"),
    ("power"),
    ("backup"),
    ("battery"),
])
def test_normals_user_should_not_access_server(loggedapp, page):
    response = loggedapp.get(reverse("server:" + page), status=302)
    assert "login" in response["Location"]


def test_staff_user_should_access_services(monkeypatch, staffapp):
    monkeypatch.setattr("subprocess.Popen", FakePopen)
    assert staffapp.get(reverse("server:services"), status=200)


def test_should_override_service_action_caller(staffapp, settings):
    spy = MagicMock()
    settings.SERVICES = [{'name': 'xxxx', 'status_caller': spy}]
    assert staffapp.get(reverse("server:services"), status=200)
    assert spy.call_count == 1


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
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    monkeypatch.setattr('ideasbox.serveradmin.backup.make_name',
                        lambda: filename)
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


def test_restore_button_should_restore(staffapp, monkeypatch, settings,
                                       backup):
    backups = os.listdir(DATA_ROOT)
    assert len(backups) == 1  # Only one backup exists.
    TEST_BACKUPED_ROOT = 'ideasbox/serveradmin/tests/backuped'
    settings.BACKUPED_ROOT = TEST_BACKUPED_ROOT
    dbpath = os.path.join(TEST_BACKUPED_ROOT, 'default.sqlite')
    assert not os.path.exists(dbpath)
    form = staffapp.get(reverse('server:backup')).forms['backup']
    form['backup'] = backup.name
    form.submit('do_restore')
    assert os.path.exists(dbpath)
    os.remove(dbpath)


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
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
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
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
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
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT',
                        BACKUPS_ROOT)
    backup_name = 'musasa_0.1.0_201501241620.zip'
    backup_path = os.path.join(BACKUPS_ROOT, backup_name)
    assert not os.path.exists(backup_path)
    with open(os.path.join(DATA_ROOT, backup_name), mode='rb') as f:
        form = staffapp.get(reverse('server:backup')).forms['backup']
        form['upload'] = Upload('badname.zip', f.read())
        resp = form.submit('do_upload')
        assert resp.status_code == 200
        assert not os.path.exists(backup_path)


def test_staff_user_should_access_battery_management(monkeypatch, staffapp):
    monkeypatch.setattr("subprocess.Popen", FakePopen)
    assert staffapp.get(reverse("server:battery"), status=200)


def test_wifi_request_corresponds_to_hotspots_list(monkeypatch,
                                                   staffapp,
                                                   list_output):
    monkeypatch.setattr("wifi.subprocess_compat.check_output", MagicMock(return_value=list_output))
    response = staffapp.get(reverse('server:wifi'))
    assert str(response.context['wifiList']) == str(Cell.all(interface, sudo=True))


def test_wifi_connection_to_hotspot(monkeypatch,
                                    staffapp,
                                    success_output,
                                    failure_output,
                                    list_output,
                                    properties_file):
    def save_mock():
        pass

    monkeypatch.setattr("wifi.scheme.Scheme.save",
                        MagicMock(side_effect=save_mock))
    monkeypatch.setattr("wifi.subprocess_compat.check_output",
                        MagicMock(return_value=list_output))
    # list hotspots
    response = staffapp.get(reverse('server:wifi'))
    hotspots = response.context['wifiList']
    assert not hotspots[0].is_connected
    assert hotspots[0].action == _('Connect')
    form = response.forms['selectWifi']
    # launch connection request
    id_ = '--'.join([hotspots[0].ssid, hotspots[0].address])
    scheme = Scheme(interface, id_)
    connection = scheme.parse_ifup_output(success_output)
    monkeypatch.setattr("wifi.scheme.Scheme.activate", MagicMock(return_value = connection))
    form.submit(hotspots[0].action)
    # assert connected
    Scheme.activate.assert_called_with()


def test_wifi_disconnection_to_hotspot(monkeypatch,
                                       staffapp,
                                       list_output,
                                       properties_file):
    monkeypatch.setattr("wifi.subprocess_compat.check_output",
                        MagicMock(return_value=list_output))
    response = staffapp.get(reverse('server:wifi'))
    hotspots = response.context['wifiList']

    def get_prop(prop, _file=properties_file):
        return getproperty(prop, _file)

    def set_props(interface_current=None,
                  scheme_current=None,
                  config=None,
                  _file=properties_file):
        kwargs = {'interface_current' : interface_current,
                  'scheme_current' : scheme_current,
                  'config' : config,
                  '_file' : _file}
        setproperties(**kwargs)

    def call_mock(args):
        pass

    monkeypatch.setattr("wifi.utils.get_property",
                        MagicMock(side_effect=get_prop))
    monkeypatch.setattr("wifi.utils.set_properties",
                        MagicMock(side_effect=set_props))
    monkeypatch.setattr("subprocess.call",
                        MagicMock(side_effect=call_mock))
    # set conditions
    # we set connect kwarg value to True to actually test disconnetion
    set_hotspots(hotspots,
                 active=1,
                 connected=True,
                 _file=properties_file,
                 interface=interface)
    # mock hotspot list
    monkeypatch.setattr("wifi.scan.Cell.all",
                        MagicMock(return_value=hotspots))
    # assert connected
    response = staffapp.get(reverse('server:wifi'))
    hotspots = response.context['wifiList']

    assert get_prop('scheme_active') == str(True)

    id_ = '--'.join([hotspots[1].ssid, hotspots[1].address])
    assert get_prop('scheme_current') == id_
    assert hotspots[1].action == _('Disconnect')
    # send request
    form = staffapp.get(reverse('server:wifi')).forms['selectWifi']
    form.submit(hotspots[1].action)
    # assert disconnected
    args = ["/sbin/ifdown", interface]
    subprocess.call.assert_called_with(args)

