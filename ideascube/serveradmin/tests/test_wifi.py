from dbus import DBusException
from mock import MagicMock
import pytest

from . import NMActiveConnection, NMConnection, NMDevice


def test_list_wifi_networks(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: []

    networks = AvailableWifiNetwork.all()
    assert list(networks.keys()) == ['my home network', 'random open network']

    assert str(networks['my home network']) == (
        'Available Wi-Fi network: "my home network"')
    assert networks['my home network'].connected is False
    assert networks['my home network'].known is False
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert networks['my home network'].strength == 99

    assert str(networks['random open network']) == (
        'Available Wi-Fi network: "random open network"')
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is False
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert networks['random open network'].strength == 42


def test_list_wifi_networks_with_one_known(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='my home network'),
        ]

    networks = AvailableWifiNetwork.all()
    assert list(networks.keys()) == ['my home network', 'random open network']

    assert str(networks['my home network']) == (
        'Available Wi-Fi network: "my home network"')
    assert networks['my home network'].connected is False
    assert networks['my home network'].known is True
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert networks['my home network'].strength == 99

    assert str(networks['random open network']) == (
        'Available Wi-Fi network: "random open network"')
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is False
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert networks['random open network'].strength == 42


def test_list_wifi_networks_with_one_connected(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = [NMActiveConnection(ssid='my home network')]
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='my home network'),
        ]

    networks = AvailableWifiNetwork.all()
    assert list(networks.keys()) == ['my home network', 'random open network']

    assert str(networks['my home network']) == (
        'Available Wi-Fi network: "my home network"')
    assert networks['my home network'].connected is True
    assert networks['my home network'].known is True
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert networks['my home network'].strength == 99

    assert str(networks['random open network']) == (
        'Available Wi-Fi network: "random open network"')
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is False
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert networks['random open network'].strength == 42


def test_list_wifi_networks_with_other_connected(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = [NMActiveConnection(ssid='my office network')]
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='my home network'),
        ]

    networks = AvailableWifiNetwork.all()
    assert list(networks.keys()) == ['my home network', 'random open network']

    assert str(networks['my home network']) == (
        'Available Wi-Fi network: "my home network"')
    assert networks['my home network'].connected is False
    assert networks['my home network'].known is True
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert networks['my home network'].strength == 99

    assert str(networks['random open network']) == (
        'Available Wi-Fi network: "random open network"')
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is False
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert networks['random open network'].strength == 42


def test_connect_to_known_open_network(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    def activate_connection(connection, device, path):
        NM.ActiveConnections.append(
            NMActiveConnection(ssid=connection.ssid, is_secure=False))

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActivateConnection.side_effect = activate_connection
    NM.ActiveConnections = []
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='random open network', is_secure=False),
        ]

    networks = AvailableWifiNetwork.all()
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is True
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 0

    networks['random open network'].connect()
    assert NM.ActivateConnection.call_count == 1
    assert NMSettings.AddConnection.call_count == 0
    assert networks['random open network'].connected is True


def test_connect_to_new_open_network(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    def add_connection(settings):
        ssid = settings['802-11-wireless']['ssid']
        connection = NMConnection(True, ssid=ssid, is_secure=False)

        NMSettings.ListConnections.side_effect = lambda: [connection]
        NM.ActiveConnections.append(
            NMActiveConnection(ssid=connection.ssid, is_secure=False))

        return connection

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = []
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.AddConnection.side_effect = add_connection
    NMSettings.ListConnections.side_effect = lambda: []

    networks = AvailableWifiNetwork.all()
    assert networks['random open network'].connected is False
    assert networks['random open network'].known is False
    assert networks['random open network'].secure is False
    assert networks['random open network'].ssid == 'random open network'
    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 0

    networks['random open network'].connect()
    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 1

    assert networks['random open network'].connected is True
    assert networks['random open network'].known is True


def test_connect_to_known_wpa_network(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork

    def activate_connection(connection, device, path):
        NM.ActiveConnections.append(
            NMActiveConnection(ssid=connection.ssid))

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActivateConnection.side_effect = activate_connection
    NM.ActiveConnections = []
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='my home network'),
        ]

    networks = AvailableWifiNetwork.all()
    assert networks['my home network'].connected is False
    assert networks['my home network'].known is True
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert NM.ActivateConnection.call_count == 0

    networks['my home network'].connect()
    assert NM.ActivateConnection.call_count == 1
    assert networks['my home network'].connected is True


def test_connect_to_new_wpa_network(mocker):
    from ideascube.serveradmin.wifi import AvailableWifiNetwork, WifiError

    def add_connection(settings):
        key = settings['802-11-wireless-security']['psk']

        if key != 'the right key':
            raise DBusException(
                '802-11-wireless-security.psk: invalid value',
                name='org.freedesktop.NetworkManager.Settings.InvalidProperty'
                )

        ssid = settings['802-11-wireless']['ssid']
        connection = NMConnection(True, ssid=ssid)

        NMSettings.ListConnections.side_effect = lambda: [connection]
        NM.ActiveConnections.append(NMActiveConnection(ssid=connection.ssid))

        return connection

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = []
    NM.Devices = [NMDevice(True)]

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.AddConnection.side_effect = add_connection
    NMSettings.ListConnections.side_effect = lambda: []

    networks = AvailableWifiNetwork.all()
    assert networks['my home network'].connected is False
    assert networks['my home network'].known is False
    assert networks['my home network'].secure is True
    assert networks['my home network'].ssid == 'my home network'
    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 0

    with pytest.raises(WifiError):
        networks['my home network'].connect()

    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 0

    with pytest.raises(WifiError):
        networks['my home network'].connect('the wrong key')

    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 1

    networks['my home network'].connect('the right key')
    assert networks['my home network'].connected is True
    assert networks['my home network'].known is True

    assert NM.ActivateConnection.call_count == 0
    assert NMSettings.AddConnection.call_count == 2


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


def test_forget_wifi_connection(mocker):
    from ideascube.serveradmin.wifi import KnownWifiConnection

    def delete_connection(connection):
        current = NMSettings.ListConnections()
        current = [c for c in current if c.ssid != connection.ssid]
        NMSettings.ListConnections.side_effect = lambda: current

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.ActiveConnections = [NMActiveConnection(ssid='my home network')]
    NM.WirelessHardwareEnabled = True

    NMSettings = mocker.patch('ideascube.serveradmin.wifi.NMSettings')
    NMSettings.ListConnections.side_effect = lambda: [
        NMConnection(False),
        NMConnection(True, ssid='random open network', is_secure=False),
        NMConnection(
            True, ssid='my home network', delete_func=delete_connection),
        ]

    connections = KnownWifiConnection.all()
    assert list(connections.keys()) == [
        'my home network', 'random open network']
    assert connections['my home network'].ssid == 'my home network'
    assert connections['my home network'].secure is True
    assert connections['my home network'].connected is True

    connections['my home network'].forget()

    connections = KnownWifiConnection.all()
    assert list(connections.keys()) == ['random open network']
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


def test_get_wifi_device(mocker):
    from ideascube.serveradmin.wifi import get_wifi_device, NM_DEVICE_TYPE_WIFI

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.Devices = [NMDevice(False), NMDevice(True)]

    device = get_wifi_device()
    assert device.DeviceType == NM_DEVICE_TYPE_WIFI


def test_get_no_wifi_device(mocker):
    from ideascube.serveradmin.wifi import get_wifi_device, WifiError

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.Devices = [NMDevice(False)]

    with pytest.raises(WifiError):
        get_wifi_device()


def test_get_multiple_wifi_devices(mocker):
    from ideascube.serveradmin.wifi import get_wifi_device, WifiError

    NM = mocker.patch('ideascube.serveradmin.wifi.NetworkManager')
    NM.Devices = [NMDevice(True), NMDevice(True)]

    with pytest.raises(WifiError):
        get_wifi_device()
