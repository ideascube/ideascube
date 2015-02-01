import re

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation.trans_real import language_code_prefix_re

register = template.Library()


SLUGS = {
    'Content': 'blog'
}
THEMES = {
    'Book': 'read',
    'Content': 'create'
}


@register.filter(is_safe=True)
def theme_slug(inst, slug=None):
    tpl = '<span class="theme {klass}">{slug}</span>'
    name = inst.__class__.__name__
    if not slug:
        slug = SLUGS.get(name, name.lower())
    klass = THEMES.get(name, slug)
    return mark_safe(tpl.format(klass=klass, slug=slug))


i18n_pattern = re.compile(language_code_prefix_re)


@register.filter()
def remove_i18n(url):
    """Remove i18n prefix from an URL."""
    return i18n_pattern.sub("/", url)
