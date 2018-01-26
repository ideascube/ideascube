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
        'preview' : "/media/"+str(inst.preview) if inst.preview else None,
        'icon' :
            "/static/"+default_preview_url(inst) if not inst.preview else None,
    }

    return json.dumps(d)
