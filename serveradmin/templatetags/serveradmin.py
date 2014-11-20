from django import template

register = template.Library()


@register.inclusion_tag('serveradmin/service_form.html')
def service_form(service):
    return service
