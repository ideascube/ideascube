try:
    from NetworkManager import (
        NM_DEVICE_TYPE_ETHERNET, NM_DEVICE_TYPE_WIFI,
        NM_ACTIVE_CONNECTION_STATE_ACTIVATED,
        )

except Exception:
    # Use hard-coded values for the tests, these are constants anyway
    NM_DEVICE_TYPE_ETHERNET = 1
    NM_DEVICE_TYPE_WIFI = 2
    NM_ACTIVE_CONNECTION_STATE_ACTIVATED = 2

from dbus import String


# This simulates DBus services, their methods and properties
FAKE_DBUS = {
    'org.freedesktop.systemd1': {
        '/org/freedesktop/systemd1': {
            'org.freedesktop.systemd1.Manager': {
                'methods': {
                    'LoadUnit': {
                        'foobar.service': '/org/freedesktop/systemd1/unit/foobar_2eservice',
                        'NetworkManager.service': '/org/freedesktop/systemd1/unit/NetworkManager_2eservice',
                        'nginx.service': '/org/freedesktop/systemd1/unit/nginx_2eservice',
                    },
                },
            },
        },
        '/org/freedesktop/systemd1/unit/foobar_2eservice': {
            'org.freedesktop.systemd1.Unit': {
                'properties': {
                    'org.freedesktop.systemd1.Unit': {
                        'Id': String('foobar.service'),
                        'LoadState': String('not-found'),
                    },
                },
            },
        },
        '/org/freedesktop/systemd1/unit/nginx_2eservice': {
            'org.freedesktop.systemd1.Unit': {
                'properties': {
                    'org.freedesktop.systemd1.Unit': {
                        'ActiveState': String('inactive'),
                        'Id': String('nginx.service'),
                        'LoadState': String('loaded'),
                    },
                },
            },
        },
        '/org/freedesktop/systemd1/unit/NetworkManager_2eservice': {
            'org.freedesktop.systemd1.Unit': {
                'properties': {
                    'org.freedesktop.systemd1.Unit': {
                        'ActiveState': String('active'),
                        'Id': String('NetworkManager.service'),
                        'LoadState': String('loaded'),
                    },
                },
            },
        },
    },
}


class FakeBus(object):
    def get_object(self, name, object_path):
        return FakeProxy(name, object_path)


class FakeProxy(object):
    def __init__(self, name, object_path):
        self.name = name
        self.object_path = object_path

        self.fake_dbus = FAKE_DBUS[self.name][self.object_path]

    def get_dbus_method(self, method, interface):
        def funcmaker(values):
            def func(*args, **_):
                value = values

                for arg in args:
                    value = value[arg]

                return value

            return func

        if method in ('Get', 'GetAll'):
            return funcmaker(self.fake_dbus[interface]['properties'])

        elif method == 'LoadUnit':
            return funcmaker(self.fake_dbus[interface]['methods'][method])

        raise ValueError(
            "Can't handle this:\n"
            " name: %s\n object path: %s\n method: %s\n interface: %s\n"
            % (self.name, self.object_path, method, interface))


class FakePopen(object):
    returncode = 0

    def __init__(self, cmd, stdout=None, stderr=None):
        self.cmd = cmd
        self.stdout = stdout()
        self.stderr = stderr()

    def communicate(self):
        if self.returncode and self.stderr is not None:
            self.stderr.write(b'Oh Noes!')

        return self.stdout.getvalue(), self.stderr.getvalue()


class NMAccessPoint(object):
    def __init__(self, ssid, strength, wpa_flags):
        self.Ssid = ssid
        self.Strength = strength
        self.WpaFlags = wpa_flags
        self.RsnFlags = wpa_flags
        self.Frequency = 5000


class NMActiveConnection(object):
    def __init__(self, ssid='', is_secure=True):
        self.Connection = NMConnection(True, ssid=ssid, is_secure=is_secure)
        self.State = NM_ACTIVE_CONNECTION_STATE_ACTIVATED


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

    def SpecificDevice(self):
        return NMSpecificDevice()


class NMSpecificDevice(object):
    def GetAllAccessPoints(self):
        return [
            NMAccessPoint('random open network', 42, 0),
            NMAccessPoint('', 2, 332),
            NMAccessPoint('my home network', 99, 332)]
