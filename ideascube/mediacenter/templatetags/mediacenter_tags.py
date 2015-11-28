from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()


@register.filter()
def preview_url(inst):
    """Do its best to return a preview URL that makes sense according to
    document instance given as parameter."""
    if inst.preview:
        return inst.preview.url
    elif inst.kind == inst.IMAGE:
        return inst.original.url
    else:
        if inst.kind == inst.OTHER:
            return static('mediacenter/document.svg')
        return static('mediacenter/default_{}.png'.format(inst.kind))
