from django import template

from ideastube.monitoring.models import InventorySpecimen

register = template.Library()


@register.assignment_tag()
def get_inventory_specimen(inventory, specimen):
    try:
        return InventorySpecimen.objects.get(inventory=inventory,
                                             specimen=specimen)
    except InventorySpecimen.DoesNotExist:
        return None
