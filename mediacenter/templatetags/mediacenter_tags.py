from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()


@register.filter()
def preview_url(inst):
    if inst.preview:
        return inst.preview.url
    elif inst.type == inst.IMAGE:
        return inst.original.url
    else:
        return static('mediacenter/document.svg')
