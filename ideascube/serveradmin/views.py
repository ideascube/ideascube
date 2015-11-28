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
from .forms import WPAConfigForm
from .wifi import (
    AvailableWifiNetwork, KnownWifiConnection, enable_wifi, WifiError, WPAConfig)


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


@staff_member_required
def wpa_config(request):
    config = WPAConfig()
    initial={'passphrase': config.get_passphrase(),
             'enable': config.is_enable}
    form = WPAConfigForm(request.POST or initial)
    if request.POST and form.is_valid():
        passphrase = form.cleaned_data['passphrase']
        enable = form.cleaned_data['enable']
        if passphrase:
            config.change_passphrase(passphrase)
        if enable:
            config.enable()
            message = _('Hotspot is now enabled with passphrase {0}').format(passphrase)
        else:
            config.disable()
            message = _('Hotspot is now disabled')
        messages.success(request, message)
    return render(
        request, 'serveradmin/wpa_config.html',
        {'form': form})
