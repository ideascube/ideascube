from collections import OrderedDict
from operator import attrgetter

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
        )

except Exception as e:
    # Set these to None so they exist, the code will handle exceptions.
    #
    # It also helps with unit tests, which wouldn't be able to mock them as
    # easily if they didn't exist here.
    NetworkManager = None
    NMSettings = None


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
