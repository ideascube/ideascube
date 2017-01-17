from django.forms import widgets

from ideascube.configuration import get_config


class ComboBoxEntry(widgets.MultiWidget):
    def __init__(self, choices, blank=False, attrs=None):
        if blank:
            choices = (('', '---------'), ) + choices

        if attrs is None:
            attrs = {}

        attrs.setdefault('autocomplete', 'off')

        self._choices = choices
        _widgets = (
            widgets.HiddenInput(attrs=attrs),
            widgets.TextInput(attrs=attrs),
        )

        super().__init__(_widgets, attrs=attrs)

    def decompress(self, value):
        if value is not None:
            for choice_id, choice_label in self._choices:
                if value == choice_id:
                    return [choice_id, choice_label]

        return [None, None]

    def value_from_datadict(self, data, files, name):
        field_name = '%s_0' % name  # The hidden input has the real value

        return data.get(field_name, '')

    def format_output(self, rendered_widgets):
        # We can't have any kind of white space between the input and the
        # button, or else browsers display a space we can't remove :(
        rendered_widgets[1] += (
            '<button class="button" type="button">▾</button>')

        rendered_widgets.insert(0, '<div class="comboboxentry">')
        rendered_widgets.append('<ul>')
        rendered_widgets.extend([
            '<li data-value="%s">%s</li>' % (o[0], o[1]) for o in self._choices
        ])
        rendered_widgets.append('</ul>')
        rendered_widgets.append('</div>')

        return '\n'.join(rendered_widgets)


class LangSelect(widgets.Select):
    def render_options(self, selected_choices):
        local_languages = get_config('content', 'local-languages')

        if local_languages is not None:
            tmp = []

            for code, name in self.choices:
                if code is '':
                    tmp.append((code, name))

                elif code in local_languages:
                    tmp.append((code, name))

                elif code in selected_choices:
                    tmp.append((code, name))

            self.choices = tmp

        return super().render_options(selected_choices)

    def render_option(self, selected_choices, option_value, option_label):
        if option_value:
            option_label = '{} ({})'.format(option_label, option_value)
        return super().render_option(selected_choices, option_value,
                                     option_label)
