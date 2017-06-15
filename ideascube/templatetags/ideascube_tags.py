import re

from django import template
from django.db.models import Count
from django.db.models.fields import FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation.trans_real import language_code_prefix_re
from django.utils.datastructures import MultiValueDict
from django.http import QueryDict

from taggit.models import Tag, ContentType

register = template.Library()


SLUGS = {
    'Content': 'blog'
}
THEMES = {
    'Book': 'read',
    'Content': 'create',
    'Document': 'discover'
}


@register.filter(is_safe=True)
def theme_slug(inst, slug=None):
    tpl = '<span class="theme {klass}">{slug}</span>'
    name = inst.__class__.__name__
    if not slug:
        slug = getattr(inst, 'slug', SLUGS.get(name, name.lower()))
    klass = THEMES.get(name, slug)
    return mark_safe(tpl.format(klass=klass, slug=slug))


i18n_pattern = re.compile(language_code_prefix_re)


@register.filter()
def remove_i18n(url):
    """Remove i18n prefix from an URL."""
    return i18n_pattern.sub("/", url)


@register.inclusion_tag('ideascube/includes/field.html')
def form_field(field):
    return {
        'field': field,
    }


@register.simple_tag
def fa(fa_id, extra_class=''):
    tpl = '<span class="fa fa-{id}{extra}"></span>'
    if extra_class:
        extra_class = ' ' + extra_class
    return mark_safe(tpl.format(id=fa_id, extra=extra_class))


@register.inclusion_tag('ideascube/includes/tag_cloud.html',
                        takes_context=True)
def tag_cloud(context, url, model=None, limit=20, tags=None):
    if not tags:
        qs = Tag.objects.all()
        if model:
            content_type = ContentType.objects.get_for_model(model)
            qs = qs.filter(taggit_taggeditem_items__content_type=content_type)
        qs = qs.annotate(count=Count('taggit_taggeditem_items__id'))
        tags = qs.order_by('-count', 'slug')[:limit]
    return {'tags': tags, 'url': url, 'request': context.request}


@register.filter()
def tag_name(slug):
    tag = Tag.objects.filter(slug=slug).first()
    return tag.name if tag else slug


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
        field = model._meta.get_field(name)
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


@register.filter()
def smart_truncate(s, length=100, suffix=u'…'):
    if len(s) > length:
        s = s[:length+1-len(suffix)]
        if ' ' in s:
            s = u' '.join(s.split(u' ')[0:-1])
        else:
            s = s[:-1]
        # We don't want to add a punctuation after another punctuation.
        while not s[-1].isalnum():
            s = s[:-1]
        s = s + suffix
    return s


@register.simple_tag
def paginate(request, **kwargs):
    get = request.GET.copy()
    for key, value in kwargs.items():
        get[key] = value
    return '?{}'.format(get.urlencode())


@register.assignment_tag(takes_context=True)
def is_in_qs(context, key, value):
    req = template.Variable('request').resolve(context)
    return _is_in_qs(req.GET.copy(), key, value)

def _is_in_qs(params, key, value):
    return key in params and value in params.getlist(key)

@register.simple_tag(takes_context=True)
def add_qs(context, *args, **kwargs):
    req = template.Variable('request').resolve(context)
    params = _add_qs(req.GET.copy(), *args, **kwargs)
    return '?%s' % params.urlencode()

def _add_qs(params, *args, **kwargs):
    for key in args:
        if not params.getlist(key):
            params[key] = 'true'
    for key, value in kwargs.items():
        if value not in params.getlist(key):
            params.appendlist(key, value)
    params.pop('page', None)  # Changing search context, reset page.
    return params

@register.simple_tag(takes_context=True)
def replace_qs(context, **kwargs):
    req = template.Variable('request').resolve(context)
    params = _replace_qs(req.GET.copy(), **kwargs)
    return '?%s' % params.urlencode()


def _replace_qs(params, **kwargs):
    for key, value in kwargs.items():
        params[key] = value
    params.pop('page', None)  # Changing search context, reset page.
    return params


@register.simple_tag(takes_context=True)
def remove_qs(context, *args, **kwargs):
    req = template.Variable('request').resolve(context)
    params = _remove_qs(req.GET.copy(), *args, **kwargs)
    return '?%s' % params.urlencode()


def _remove_qs(params, *args, **kwargs):
    existing = dict(params)
    for key in args:
        try:
            del existing[key]
        except KeyError:
            pass
    for key, value in kwargs.items():
        try:
            existing[key].remove(value)
        except (KeyError, ValueError):
            pass
        else:
            if not existing[key]:
                del existing[key]
    params = QueryDict(mutable=True)
    params.update(MultiValueDict(existing))
    params.pop('page', None)  # Changing search context, reset page.
    return params


@register.simple_tag
def media(instance, attribute):
    url = getattr(instance, attribute).url
    qs = 'mtime={0.modified_at:%Y-%m-%dT%H:%M:%S%Z}'.format(instance)

    return '%s?%s' % (url, qs)
