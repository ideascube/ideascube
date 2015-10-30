from collections import OrderedDict
from itertools import groupby
from operator import attrgetter
from uuid import uuid4

from django.utils.translation import ugettext as _

try:
    # The NetworkManager module tries to connect to the NetworkManager daemon
    # right when we import it.
    #
    # Therefore, if there is no NetworkManager daemon running, or if it isn't
    # reachable for some reason (like in our CI servers), the imports will
    # fail.
    from NetworkManager import (
        NetworkManager,
        Settings as NMSettings,
        NM_DEVICE_TYPE_WIFI,
        )

except Exception as e:
    # Set these to None so they exist, the code will handle exceptions.
    #
    # It also helps with unit tests, which wouldn't be able to mock them as
    # easily if they didn't exist here.
    NetworkManager = None
    NMSettings = None

    # Hardcode this one, it is a constant anyway in the NetworkManager module,
    # and hardcoding it allows the tests to run no matter what.
    NM_DEVICE_TYPE_WIFI = 2


class AvailableWifiNetwork(object):
    @classmethod
    def all(cls):
        result = []

        known_connections = KnownWifiConnection.all()

        device = get_wifi_device()
        aps = device.SpecificDevice().GetAllAccessPoints()
        aps.sort(key=attrgetter('Frequency'), reverse=True)
        aps.sort(key=attrgetter('Ssid'))

        for ssid, grouper in groupby(aps, attrgetter('Ssid')):
            if ssid:
                # There often are more than one network for a given SSID (for
                # example at 2.4 and 5GHz), so we keep only the one with the
                # highest frequency.
                ap = next(grouper)
                result.append(cls(ap, device, known_connections))

        return OrderedDict(
            [(n.ssid, n) for n in sorted(
                result, key=attrgetter('strength'), reverse=True)])

    def __init__(self, access_point, device, known_connections=None):
        self._access_point = access_point
        self._device = device

        known_connections = known_connections or {}
        self._connection = known_connections.get(self.ssid, None)

    def __str__(self):
        return 'Available Wi-Fi network: "%s"' % (self.ssid)

    def _new_connection(self):
        settings = {
            'connection': {
                'autoconnect': True,
                'id': self.ssid,
                'type': '802-11-wireless',
                'uuid': str(uuid4()),
                },
            '802-11-wireless': {
                'mode': 'infrastructure',
                'ssid': self.ssid,
                },
            'ipv4': {
                'method': 'auto'
                },
            'ipv6': {
                'method': 'auto'
                }
            }

        return KnownWifiConnection(NMSettings.AddConnection(settings))

    def connect(self):
        if self._connection is not None:
            NetworkManager.ActivateConnection(
                self._connection._connection, self._device, "/")

        else:
            self._connection = self._new_connection()

    @property
    def connected(self):
        return self._connection and self._connection.connected or False

    @property
    def known(self):
        return self._connection is not None

    @property
    def secure(self):
        return self._access_point.WpaFlags != 0

    @property
    def ssid(self):
        return self._access_point.Ssid

    @property
    def strength(self):
        return self._access_point.Strength


class KnownWifiConnection(object):
    @classmethod
    def all(cls):
        result = []

        for connection in NMSettings.ListConnections():
            if '802-11-wireless' not in connection.GetSettings():
                continue

            result.append(cls(connection))

        return OrderedDict(
            [(c.ssid, c) for c in sorted(result, key=attrgetter('ssid'))])

    def __init__(self, connection):
        self._connection = connection

    def __str__(self):
        return 'Known Wi-Fi connection: "%s"' % (self.ssid)

    @property
    def connected(self):
        for active_connection in NetworkManager.ActiveConnections:
            if (active_connection.Connection.GetSettings()
                    == self._connection.GetSettings()):
                return True

        return False

    @property
    def secure(self):
        return '802-11-wireless-security' in self._connection.GetSettings()

    @property
    def ssid(self):
        return self._connection.GetSettings()['802-11-wireless']['ssid']


class WifiError(Exception):
    pass


def enable_wifi():
    try:
        if not NetworkManager.WirelessHardwareEnabled:
            raise WifiError(_("Wi-Fi hardware is disabled"))

        NetworkManager.WirelessEnabled = True

    except WifiError:
        raise

    except:
        # This will fail if NetworkManager is None, i.e we couldn't import it
        raise WifiError(_("Wi-Fi is disabled"))


def get_wifi_device():
    devices = []

    for device in NetworkManager.Devices:
        if device.Managed and device.DeviceType == NM_DEVICE_TYPE_WIFI:
            devices.append(device)

    if not devices:
        raise WifiError(_("No Wi-Fi device was found"))

    if len(devices) > 1:
        raise WifiError(
            _("Found more than one Wi-Fi device, this is not supported"))

    return devices[0]
