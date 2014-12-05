from subprocess import call

from django.conf import settings
from django.shortcuts import render

from .utils import call_service


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
        service_return = call_service(service)
        service['error'] = service_return.get('error')
        service['status'] = service_return.get('status')
    return render(request, 'serveradmin/services.html', {'services': services})


def server(request):
    if request.POST:
        if 'stop' in request.POST:
            call(["sudo", "poweroff"])
        elif 'restart' in request.POST:
            call(["sudo", "reboot"])

    return render(request, 'serveradmin/server.html')
