from subprocess import call

import batinfo
from wifi import Cell, Scheme
from wifi.exceptions import ConnectionError, InterfaceError
from wifi.utils import get_property, set_properties

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from .backup import Backup
from .utils import call_service

interface = 'wlan0'

@staff_member_required
def services(request):
    services = settings.SERVICES
    service_action = 'status'
    if request.POST:
        active_service = request.POST['name']
        if 'start' in request.POST:
            service_action = 'start'
        elif 'stop' in request.POST:
            service_action = 'stop'
        elif 'restart' in request.POST:
            service_action = 'restart'
    else:
        active_service = None

    for service in services:
        if active_service == service['name']:
            service['action'] = service_action
        else:
            service['action'] = 'status'
        # The way to run the action may be overrided in the service definition
        # in the settings.
        caller = '{action}_caller'.format(**service)
        if caller in service:
            status = service[caller](service)
        else:
            status = call_service(service)
        service['error'] = status.get('error')
        service['status'] = status.get('status')
    return render(request, 'serveradmin/services.html', {'services': services})


@staff_member_required
def power(request):
    if request.POST:
        if 'stop' in request.POST:
            call(["sudo", "poweroff"])
        elif 'restart' in request.POST:
            call(["sudo", "reboot"])

    return render(request, 'serveradmin/power.html')


@staff_member_required
def backup(request):
    if request.POST:
        if 'do_create' in request.POST:
            backup = Backup.create()
            msg = _('Succesfully created backup {filename}').format(
                filename=backup.name
            )
            messages.add_message(request, messages.SUCCESS, msg)
        elif 'do_upload' in request.POST:
            if 'upload' in request.FILES:
                file_ = request.FILES['upload']
                try:
                    backup = Backup.load(file_)
                except Exception as e:
                    msg = _('Unable to load file:')
                    msg = "{msg} {error}".format(msg=msg, error=e.message)
                    messages.add_message(request, messages.ERROR, msg)
                else:
                    msg = _('File {name} has been loaded.').format(
                        name=backup.name)
                    messages.add_message(request, messages.SUCCESS, msg)
            else:
                messages.add_message(request, messages.ERROR,
                                     _('No file found to upload.'))
        elif 'backup' in request.POST:
            backup = Backup(request.POST['backup'])
            msg = None
            if 'do_delete' in request.POST:
                backup.delete()
                msg = _('Succesfully deleted backup {filename}').format(
                    filename=backup.name
                )
            elif 'do_restore' in request.POST:
                backup.restore()
                msg = _('Succesfully restored backup {filename}').format(
                    filename=backup.name
                )
            elif 'do_download' in request.POST:
                response = StreamingHttpResponse(open(backup.path, 'rb'))
                cd = 'attachment; filename="{name}"'.format(name=backup.name)
                response['Content-Disposition'] = cd
                return response
            if msg:
                messages.add_message(request, messages.SUCCESS, msg)
    context = {
        'backups': Backup.list()
    }
    return render(request, 'serveradmin/backup.html', context)


@staff_member_required
def battery(request):
    return render(request, 'serveradmin/battery.html',
                  {'batteries': batinfo.batteries()})


def set_wifilist():
    to_bool = {'True' : True, 'False' : False, None : False, 'None' : False}
    # reset scheme_active property
    essid = get_property('scheme_current').split('--')[0]
    try:
        is_essid = to_bool[essid]
    except KeyError:
        is_essid = True
    if is_essid:
        options = {'wireless-essid' : essid}
    else:
        options = None
    set_properties(None, None, options)
    is_connected = to_bool[get_property('scheme_active')] or False
    action = {True : _('Disconnect'), False : _('Connect')}
    try:
        wifi = Cell.all(interface, sudo=True)
        # Florian --> config file with interface name
        for hotspot in wifi:
            # find out if connected with
            id_ = '--'.join([hotspot.ssid, hotspot.address])
            hotspot.is_active = (get_property('scheme_current') == id_)
            hotspot.is_connected = (hotspot.is_active and is_connected)
            hotspot.action = action[hotspot.is_connected]
    except InterfaceError:
        wifi = ""
    return wifi, is_connected


@staff_member_required
def wifi(request):
    set_wifilist()
    if request.POST:
        action_ = request.POST['action']
        if action_ == _('Connect'):
            # we use the addresses to set unicity of the schemes created
            address = request.POST['address']
            cell_kwargs = {'interface' : interface,
                           'name' : '--'.join([request.POST['ssid'], address]),
                           'passkey' : request.POST['key']}
            cell = Cell.where(cell_kwargs['interface'],
                              lambda cell: cell.address == address)[0]
            cell_kwargs['cell'] = cell
            scheme = Scheme.for_cell(**cell_kwargs)
            if not Scheme.find(cell_kwargs['interface'], scheme.name):
                scheme.save()
            try:
                scheme.activate()
            except ConnectionError:
                # just to verify in terminal
                print "erreur"
        else:
            # disconnect
            call(["sbin/ifdown", interface])
    return render(request, 'serveradmin/wifi.html',
                  {'wifiList': set_wifilist()[0],
                   'AuthOK' : set_wifilist()[1]})

