from select_multiple_field.models import SelectMultipleField
from django.forms import CheckboxSelectMultiple


class CommaSeparatedCharField(SelectMultipleField):

    def contribute_to_class(self, cls, name, **kwargs):
        """Contribute to the Model subclass.

        We just set our custom get_FIELD_display(),
        which returns a comma-separated list of displays.
        """
        super().contribute_to_class(cls, name, **kwargs)

        def _get_FIELD_display(instance):
            choices = dict(self.choices)
            values = getattr(instance, self.attname)
            return ", ".join(str(choices.get(c, c)) for c in values if c)

        setattr(cls, 'get_%s_display' % self.name, _get_FIELD_display)

    def formfield(self, **kwargs):
        kwargs['widget'] = CheckboxSelectMultiple
        return super().formfield(**kwargs)

    def get_choices(self, **kwargs):
        kwargs['include_blank'] = False
        return super().get_choices(**kwargs)
