from django.conf import settings
from django.shortcuts import render

from .utils import call_service


def services(request):
    services = settings.SERVICES
    if request.POST:
        service_name = request.POST['name']
        if 'start' in request.POST:
            service_action = 'start'
        elif 'stop' in request.POST:
            service_action = 'stop'
        elif 'restart' in request.POST:
            service_action = 'restart'
    else:
        service_name = False

    for service in services:
        if service_name == service['name']:
            service['action'] = service_action
        else:
            service['action'] = 'status'
        service_return = call_service(service)
        service['error'] = service_return.get('error')
        service['status'] = service_return.get('status')
    return render(request, 'serveradmin/services.html', {'services': services})
