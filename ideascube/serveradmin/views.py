from subprocess import call

import batinfo
from django.conf import settings
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from ideascube.decorators import staff_member_required
from ideascube.models import Setting

from .backup import Backup
from .systemd import Manager, NoSuchUnit, UnitManagementError
from .wifi import (
    AvailableWifiNetwork, KnownWifiConnection, enable_wifi, WifiError)


@staff_member_required
def server_name(request):
    if request.method == 'POST':
        new_name = request.POST.get('server_name')

        if new_name:
            Setting.set('server', 'site-name', new_name, request.user)

        else:
            messages.error(request, _('Server name cannot be empty'))

    return render(request, 'serveradmin/name.html')


@staff_member_required
def services(request):
    services = settings.SERVICES
    manager = Manager()
    to_manage = request.POST.get('name')

    for service in services:
        # Reset these, otherwise the values are cached from a previous run.
        service['status'] = False
        service['error'] = None

        name = service['name']

        try:
            service_unit = manager.get_service(service['name'])

            if name == to_manage:
                if 'start' in request.POST:
                    manager.activate(service_unit.Id)

                elif 'stop' in request.POST:
                    manager.deactivate(service_unit.Id)

                elif 'restart' in request.POST:
                    manager.restart(service_unit.Id)

            service['status'] = service_unit.active

        except NoSuchUnit:
            service['error'] = 'Not installed'

        except UnitManagementError as e:
            messages.error(request, e)

    return render(
        request, 'serveradmin/services.html', {'services': services})


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
                    msg = "{msg} {error}".format(msg=msg, error=str(e))
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


@staff_member_required
def wifi(request, ssid=''):
    try:
        enable_wifi()
        wifi_list = AvailableWifiNetwork.all()

    except WifiError as e:
        messages.error(request, e)
        return render(request, 'serveradmin/wifi.html')

    if ssid:
        try:
            network = wifi_list[ssid]
            wifi_key = request.POST.get('wifi_key', '')
            network.connect(wifi_key=wifi_key)
            messages.success(
                request, _('Connected to {ssid}').format(ssid=ssid))

        except KeyError:
            messages.error(
                request, _('No such network: {ssid}').format(ssid=ssid))

        except WifiError as e:
            messages.error(request, e)

    return render(
        request, 'serveradmin/wifi.html', {'wifi_list': wifi_list.values()})


@staff_member_required
def wifi_history(request):
    try:
        enable_wifi()
        wifi_list = KnownWifiConnection.all()

    except WifiError as e:
        messages.error(request, e)
        return render(request, 'serveradmin/wifi_history.html')

    for ssid, checked in request.POST.items():
        if checked.lower() in ('on', 'true'):
            try:
                connection = wifi_list.pop(ssid)
                connection.forget()

            except KeyError:
                # Someone tried to forget a connection we don't know.
                continue

    return render(
        request, 'serveradmin/wifi_history.html',
        {'wifi_list': wifi_list.values()})
