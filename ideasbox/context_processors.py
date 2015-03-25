from django.conf import settings as djsettings

from ideasbox import __version__


def settings(request):
    keys = ['IDEASBOX_NAME']
    return {k: getattr(djsettings, k) for k in keys}


def version(request):
    return {'IDEASBOX_VERSION': __version__}
