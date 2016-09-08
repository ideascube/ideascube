from django.conf import settings as djsettings

from ideascube import __version__
from ideascube.configuration import get_config


def favicon_url(request):
    box_type = djsettings.IDEASCUBE_BOX_TYPE
    return {'favicon_url': 'ideascube/img/favicons/%s.png' % box_type}


def server(request):
    return {'server_name': get_config('server', 'site-name')}


def settings(request):
    keys = ['IDEASCUBE_BOX_TYPE', 'IDEASCUBE_ID',
            'IDEASCUBE_HOSTNAME', 'LANG_INFO']
    return {k: getattr(djsettings, k) for k in keys}


def version(request):
    return {'IDEASCUBE_VERSION': __version__}
