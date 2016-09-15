from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()


@register.filter
def default_preview_url(inst):
    return static('mediacenter/default_{}.png'.format(inst.kind))
