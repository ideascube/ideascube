from django import template
import json

register = template.Library()


@register.filter
def default_preview_url(inst):
    return 'mediacenter/default_{}.png'.format(inst.kind)

@register.filter
def to_json_dict(inst):
    d = {
        'kind': inst.kind,
        'original': "/media/"+str(inst.original),
        'url': inst.get_absolute_url(),
    }
    if inst.preview:
        d['icon'] = "/media/"+str(inst.preview)
    elif inst.kind == inst.IMAGE:
        d['icon'] = "/media/"+str(inst.original)
    else:
        d['icon'] = "/static/"+default_preview_url(inst)

    return json.dumps(d)
