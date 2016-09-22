from django import template

register = template.Library()


@register.filter
def default_preview_url(inst):
    return 'mediacenter/default_{}.png'.format(inst.kind)
