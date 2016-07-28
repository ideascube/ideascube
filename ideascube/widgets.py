from django.forms import widgets

from ideascube.configuration import get_config


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
