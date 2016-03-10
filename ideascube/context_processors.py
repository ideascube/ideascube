from django.conf import settings as djsettings

from ideascube import __version__


def settings(request):
    keys = ['IDEASCUBE_NAME', 'IDEASCUBE_BODY_ID', 'IDEASCUBE_ID',
            'IDEASCUBE_HOSTNAME', 'LANG_INFO']
    return {k: getattr(djsettings, k) for k in keys}


def version(request):
    return {'IDEASCUBE_VERSION': __version__}
