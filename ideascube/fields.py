from django import forms

from select_multiple_field.models import SelectMultipleField


class CommaSeparatedCharField(SelectMultipleField):

    def contribute_to_class(self, cls, name, **kwargs):
        """Contribute to the Model subclass.

        We just set our custom get_FIELD_display(),
        which returns a comma-separated list of displays.
        """
        super(CommaSeparatedCharField, self).contribute_to_class(cls, name,
                                                                 **kwargs)

        def _get_FIELD_display(instance):
            choices = dict(self.choices)
            values = getattr(instance, self.attname)
            return ", ".join(str(choices.get(c, c)) for c in values if c)

        setattr(cls, 'get_%s_display' % self.name, _get_FIELD_display)


class LangSelect(forms.Select):

    def render_option(self, selected_choices, option_value, option_label):
        if option_value:
            option_label = '{} ({})'.format(option_label, option_value)
        return super().render_option(selected_choices, option_value,
                                     option_label)
