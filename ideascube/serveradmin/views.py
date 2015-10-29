from subprocess import call

import batinfo
from django.conf import settings
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from ideascube.decorators import staff_member_required

from .backup import Backup
from .utils import call_service
from .wifi import AvailableWifiNetwork, enable_wifi, WifiError


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
