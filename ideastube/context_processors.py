from django.conf import settings as djsettings

from ideastube import __version__


def settings(request):
    keys = ['IDEASTUBE_NAME', 'IDEASTUBE_BODY_ID']
    return {k: getattr(djsettings, k) for k in keys}


def version(request):
    return {'IDEASTUBE_VERSION': __version__}
