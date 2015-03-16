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
            return ", ".join(choices[c] for c in values)

        setattr(cls, 'get_%s_display' % self.name, _get_FIELD_display)
