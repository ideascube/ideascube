from django.conf import settings as djsettings

from ideascube import __version__
from ideascube.utils import get_server_name


def server(request):
    return {'server_name': get_server_name()}


def settings(request):
    keys = ['IDEASCUBE_BODY_ID', 'IDEASCUBE_ID',
            'IDEASCUBE_HOSTNAME', 'LANG_INFO']
    return {k: getattr(djsettings, k) for k in keys}


def version(request):
    return {'IDEASCUBE_VERSION': __version__}
