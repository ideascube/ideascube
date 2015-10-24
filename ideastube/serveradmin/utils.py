import subprocess


def call_service(service):
    args = ['sudo', 'service', service['name'], service['action']]
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    to_return = {'status': True}
    if process.returncode:
        to_return = {'status': False}
        if stderr:
            to_return['error'] = stderr
    return to_return
