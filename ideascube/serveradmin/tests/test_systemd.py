import pytest

from . import FakeBus


def test_get_service(mocker):
    from ideascube.serveradmin.systemd import Manager

    mocker.patch(
        'ideascube.serveradmin.systemd.dbus.SystemBus', side_effect=FakeBus)

    manager = Manager()

    service = manager.get_service('NetworkManager.service')
    assert service.LoadState == 'loaded'
    assert service.ActiveState == 'active'
    assert service.active

    service = manager.get_service('NetworkManager')
    assert service.LoadState == 'loaded'
    assert service.ActiveState == 'active'
    assert service.active


def test_get_no_such_service(mocker):
    from ideascube.serveradmin.systemd import Manager, NoSuchUnit

    mocker.patch(
        'ideascube.serveradmin.systemd.dbus.SystemBus', side_effect=FakeBus)

    manager = Manager()

    with pytest.raises(NoSuchUnit):
        manager.get_service('foobar')


def test_unit(mocker):
    from ideascube.serveradmin.systemd import Unit

    mocker.patch(
        'ideascube.serveradmin.systemd.dbus.SystemBus', side_effect=FakeBus)

    unit = Unit('/org/freedesktop/systemd1/unit/NetworkManager_2eservice')
    assert unit.LoadState == 'loaded'
    assert unit.ActiveState == 'active'
    assert unit.active


def test_no_such_unit(mocker):
    from ideascube.serveradmin.systemd import NoSuchUnit, Unit

    mocker.patch(
        'ideascube.serveradmin.systemd.dbus.SystemBus', side_effect=FakeBus)

    with pytest.raises(NoSuchUnit):
        Unit('/org/freedesktop/systemd1/unit/foobar_2eservice')
