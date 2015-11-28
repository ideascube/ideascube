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
        if inst.kind == inst.VIDEO:
            return static('mediacenter/default_video.png')
        elif inst.kind == inst.PDF:
            return static('mediacenter/default_pdf.png')
        elif inst.kind == inst.TEXT:
            return static('mediacenter/default_text.png')
        elif inst.kind == inst.AUDIO:
            return static('mediacenter/default_sound.png')
        else:
            return static('mediacenter/document.svg')
