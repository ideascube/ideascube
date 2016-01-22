import subprocess
import string

import dbus


class Manager(object):
    def __init__(self):
        proxy = dbus.SystemBus().get_object(
            'org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self._manager = dbus.Interface(
            proxy, dbus_interface='org.freedesktop.systemd1.Manager')

    def _get_unit(self, unit_id):
        return Unit(self._manager.LoadUnit(unit_id))

    def get_service(self, service_name):
        if not service_name.endswith('.service'):
            service_id = "%s.service" % service_name

        else:
            service_id = service_name

        return self._get_unit(service_id)

    def activate(self, unit_id):
        systemctl('enable', unit_id)
        systemctl('start', unit_id)

    def deactivate(self, unit_id):
        systemctl('disable', unit_id)
        systemctl('stop', unit_id)

    def restart(self, unit_id):
        systemctl('restart', unit_id)


class Unit(object):
    def __init__(self, path):
        proxy = dbus.SystemBus().get_object('org.freedesktop.systemd1', path)
        self._unit = dbus.Interface(
            proxy, dbus_interface='org.freedesktop.systemd1.Unit')

        props = self._unit.GetAll(
            'org.freedesktop.systemd1.Unit',
            dbus_interface=dbus.PROPERTIES_IFACE)

        for prop in props:
            prop = str(prop)

            if not hasattr(self.__class__, prop):
                setattr(self.__class__, prop, self._make_property(prop))

        if self.LoadState == 'not-found':
            raise NoSuchUnit(self.Id)

    def _make_property(self, name):
        def get_func(self):
            return dbus_to_python(self._unit.Get(
                'org.freedesktop.systemd1.Unit', name,
                dbus_interface=dbus.PROPERTIES_IFACE))

        return property(get_func)

    @property
    def active(self):
        return self.ActiveState == 'active'


class NoSuchUnit(Exception):
    pass


class UnitManagementError(Exception):
    pass


def dbus_to_python(obj):
    if isinstance(obj, dbus.String):
        return str(obj)

    # Add support for other DBus types as we need them
    raise ValueError("Can't handle value: %r" % obj)


def systemctl(action, unit):
    # TODO: Move that to the systemd dbus API if we can rely on systemd >= 216
    cmd = ['pkexec', 'systemctl', action, unit]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = proc.communicate()

    if proc.returncode:
        msg = ["Could not %s %s" % (action, unit)]

        if err:
            msg.append(err.strip().decode())

        raise UnitManagementError(': '.join(msg))
