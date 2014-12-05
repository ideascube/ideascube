from subprocess import call

from django.shortcuts import render


def server(request):
    if request.POST:
        if 'stop' in request.POST:
            call(["sudo", "poweroff"])
        elif 'restart' in request.POST:
            call(["sudo", "restart"])

    return render(request, 'serveradmin/server.html')
