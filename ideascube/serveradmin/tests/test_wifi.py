from mock import MagicMock
import pytest

from . import NMActiveConnection, NMConnection


def test_list_known_wifi_connections(mocker):
    from ideascube.serveradmin.wifi import KnownWifiConnection

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = []

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='random open network', is_secure=False),
        NMConnection(True, ssid='my home network'),
        ]

    connections = KnownWifiConnection.all()
    assert list(connections.keys()) == [
        'my home network', 'random open network']

    assert str(connections['my home network']) == (
        'Known Wi-Fi connection: "my home network"')
    assert connections['my home network'].connected is False
    assert connections['my home network'].secure is True
    assert connections['my home network'].ssid == 'my home network'

    assert str(connections['random open network']) == (
        'Known Wi-Fi connection: "random open network"')
    assert connections['random open network'].connected is False
    assert connections['random open network'].secure is False
    assert connections['random open network'].ssid == 'random open network'


def test_list_known_wifi_connections_with_one_connected(mocker):
    from ideascube.serveradmin.wifi import KnownWifiConnection

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = [NMActiveConnection(ssid='my home network')]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='random open network', is_secure=False),
        NMConnection(True, ssid='my home network'),
        ]

    connections = KnownWifiConnection.all()
    assert list(connections.keys()) == [
        'my home network', 'random open network']

    assert str(connections['my home network']) == (
        'Known Wi-Fi connection: "my home network"')
    assert connections['my home network'].ssid == 'my home network'
    assert connections['my home network'].secure is True
    assert connections['my home network'].connected is True

    assert str(connections['random open network']) == (
        'Known Wi-Fi connection: "random open network"')
    assert connections['random open network'].connected is False
    assert connections['random open network'].secure is False
    assert connections['random open network'].ssid == 'random open network'


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
