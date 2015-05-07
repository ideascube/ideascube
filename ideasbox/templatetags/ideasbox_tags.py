import re

from django import template
from django.db.models import Count
from django.db.models.fields import FieldDoesNotExist
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


@register.inclusion_tag('ideasbox/includes/field.html')
def form_field(field):
    return {
        'field': field,
    }


@register.simple_tag
def fa(fa_id, extra_class=''):
    tpl = '<span class="fa fa-{id}{extra}"></span>'
    if extra_class:
        extra_class = ' ' + extra_class
    return tpl.format(id=fa_id, extra=extra_class)


@register.inclusion_tag('ideasbox/includes/tag_cloud.html')
def tag_cloud(url, model=None, limit=20):
    qs = Tag.objects.all()
    if model:
        content_type = ContentType.objects.get_for_model(model)
        qs = qs.filter(taggit_taggeditem_items__content_type=content_type)
    qs = qs.annotate(count=Count('taggit_taggeditem_items__id'))
    return {'tags': qs.order_by('-count', 'slug')[:limit], 'url': url}


@register.filter(name='getattr')
def do_getattr(obj, attr):
    return getattr(obj, attr, None)


@register.filter(name='getitem')
def do_getitem(obj, key):
    try:
        return obj[key]
    except KeyError:
        return None


@register.filter()
def field_verbose_name(model, name):
    try:
        field, _, _, _ = model._meta.get_field_by_name(name)
    except FieldDoesNotExist:
        return ''
    else:
        return field.verbose_name


@register.filter()
def field_value_display(obj, name):
    try:
        return getattr(obj, 'get_{0}_display'.format(name))()
    except AttributeError:
        return getattr(obj, name, None)


@register.filter()
def model(obj):
    return obj.__class__


@register.filter(name='min')
def do_min(left, right):
    return min(left, right)
