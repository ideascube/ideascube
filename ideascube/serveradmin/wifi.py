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
        )

except Exception as e:
    # Set these to None so they exist, the code will handle exceptions.
    #
    # It also helps with unit tests, which wouldn't be able to mock them as
    # easily if they didn't exist here.
    NetworkManager = None


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
