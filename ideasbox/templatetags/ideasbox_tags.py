import re

from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation.trans_real import language_code_prefix_re

from taggit.models import Tag, ContentType

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


@register.inclusion_tag('ideasbox/includes/tag_cloud.html')
def tag_cloud(url, model=None, limit=20):
    qs = Tag.objects.all()
    if model:
        content_type = ContentType.objects.get_for_model(model)
        qs = qs.filter(taggit_taggeditem_items__content_type=content_type)
    qs = qs.annotate(count=Count('taggit_taggeditem_items__id'))
    return {'tags': qs.order_by('-count', 'slug')[:limit], 'url': url}
