from django.conf import settings
from django.shortcuts import render

from .utils import service_exec


def services(request):
    services = settings.SERVICES
    if request.POST:
        service_name = request.POST['title']
        for service in services:
            if service_name in service.values():
                if 'start' in request.POST:
                    service['action'] = 'start'
                elif 'stop' in request.POST:
                    service['action'] = 'stop'
                elif 'restart' in request.POST:
                    service['action'] = 'restart'

    for service in services:
        if not 'action' in service:
            service['action'] = 'status'
        service['status'] = service_exec(service)
    return render(request, 'serveradmin/services.html', {'services': services})
