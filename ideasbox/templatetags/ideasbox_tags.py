from django import template
from django.utils.safestring import mark_safe

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
    tpl = '<span class="theme {0}">{1}</span>'
    name = inst.__class__.__name__
    if not slug:
        slug = SLUGS.get(name, name.lower())
    theme = THEMES.get(name, slug)
    return mark_safe(tpl.format(theme, slug))
