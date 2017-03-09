import re
from django import template

register = template.Library()


@register.filter
def default_preview_url(inst):
    return 'mediacenter/default_{}.png'.format(inst.kind)


link_regex = re.compile(r"(https?://[^\s]+)")

@register.simple_tag
def htmlize_description(text):
    text = link_regex.sub(r'<a href="\1">\1</a>', text)
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = text.replace('\n', '<br/>')
    return text
