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
