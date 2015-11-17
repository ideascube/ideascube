import pytest

from . import FakeBus


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
