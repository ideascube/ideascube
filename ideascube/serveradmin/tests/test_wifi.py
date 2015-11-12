from mock import MagicMock, PropertyMock
import pytest


def test_enable_wifi(mocker):
    from ideascube.serveradmin.wifi import enable_wifi

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.WirelessEnabled = False
    NM.WirelessHardwareEnabled = True

    enable_wifi()
    assert NM.WirelessEnabled is True


def test_wifi_hardware_disabled(mocker):
    from ideascube.serveradmin.wifi import enable_wifi, WifiError

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.WirelessEnabled = False
    NM.WirelessHardwareEnabled = False

    with pytest.raises(WifiError):
        enable_wifi()

    assert NM.WirelessEnabled is False


def test_wifi_cannot_be_enabled(mocker):
    from ideascube.serveradmin.wifi import enable_wifi, WifiError

    class MockedNM(MagicMock):
        def __getattr__(self, name):
            raise AttributeError()

    mocker.patch('ideascube.serveradmin.wifi.NetworkManager', new=MockedNM())

    with pytest.raises(WifiError):
        enable_wifi()
