from django import template

from ideascube.monitoring.models import InventorySpecimen

register = template.Library()


@register.simple_tag()
def get_inventory_specimen(inventory, specimen):
    try:
        return InventorySpecimen.objects.get(inventory=inventory,
                                             specimen=specimen)
    except InventorySpecimen.DoesNotExist:
        return None
