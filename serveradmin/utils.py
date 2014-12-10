import subprocess

from re import match

from django.utils.translation import ugettext as _


def call_service(service):
    args = ['sudo', 'service', service['name'], service['action']]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    to_return = {'error': service['name']+': '+_('unknown error')}
    if stdout:
        if match('.*(is running|start/running).*', stdout):
            to_return = {'status': True}
        elif match('.*(not running|stop/waiting).*', stdout):
            to_return = {'status': False}
    elif stderr:
        to_return = {'error': stderr}
    return to_return
