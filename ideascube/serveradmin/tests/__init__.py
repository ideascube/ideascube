try:
    from NetworkManager import NM_DEVICE_TYPE_ETHERNET, NM_DEVICE_TYPE_WIFI

except Exception:
    # Use hard-coded values for the tests, these are constants anyway
    NM_DEVICE_TYPE_ETHERNET = 1
    NM_DEVICE_TYPE_WIFI = 2


class NMActiveConnection(object):
    def __init__(self, ssid='', is_secure=True):
        self.Connection = NMConnection(True, ssid=ssid, is_secure=is_secure)


class NMConnection(object):
    def __init__(self, is_wifi, ssid='', is_secure=True, delete_func=None):
        self.is_wifi = is_wifi
        self.is_secure = is_secure
        self.ssid = ssid

        if delete_func is not None:
            self.Delete = lambda: delete_func(self)

    def GetSettings(self):
        if not self.is_wifi:
            return {}

        settings = {'802-11-wireless': {'ssid': self.ssid}}

        if self.is_secure:
            settings.update({'802-11-wireless-security': {}})

        return settings


class NMDevice(object):
    def __init__(self, is_wifi):
        self.DeviceType = (
            NM_DEVICE_TYPE_WIFI if is_wifi else NM_DEVICE_TYPE_ETHERNET)
        self.Managed = True
