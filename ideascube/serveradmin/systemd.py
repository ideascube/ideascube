import dbus


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


def dbus_to_python(obj):
    if isinstance(obj, dbus.String):
        return str(obj)

    # Add support for other DBus types as we need them
    raise ValueError("Can't handle value: %r" % obj)
