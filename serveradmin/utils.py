from subprocess import Popen, PIPE
from re import match


def call_service(service):
    args = ['sudo', 'service', service['name'], service['action']]
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        if match('.*(is running|start/running).*', stdout):
            to_return = {'status': True, 'error': False}
        elif match('.*(not running|stop/waiting).*', stdout):
            to_return = {'status': False, 'error': False}
    elif stderr:
        to_return = {'error': stderr}
    else:
        to_return = {'error': service['name']+': unknown error'}
    return to_return
