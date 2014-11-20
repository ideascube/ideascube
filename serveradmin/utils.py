import subprocess

from re import match


def service_exec(service):
    args = ['sudo', 'service', service['name'], service['action']]
    try:
        ret = subprocess.check_output(args)
    except subprocess.CalledProcessError as ret_error:
        ret = ret_error.output

    if match('.*(is running|start/running).*', ret):
        return 'on'
    elif match('.*(not running|stop/waiting).*', ret):
        return 'off'
    else:
        if ret:
            return ret
        return 'Something odd happen here..'
