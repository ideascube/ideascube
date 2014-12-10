from django.conf import settings as djsettings


def settings(request):
    keys = ['RTL_LANGUAGES', 'IDEASBOX_NAME']
    return {k: getattr(djsettings, k) for k in keys}
