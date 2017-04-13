from django.forms import widgets

from ideascube.configuration import get_config
from django.utils.html import mark_safe, escape
from django.utils.encoding import force_text
from django.forms.utils import flatatt
from django.utils.translation import get_language

import bleach


_ideascube_to_tinyMCE_language_map = {
    'fr': 'fr_FR'
}


class RichTextEntry(widgets.Widget):
    def __init__(self, *, with_media=False, attrs=None):
        super().__init__(attrs=attrs)
        self.with_media = with_media

        self.authorized_tags = [
            'p', 'a', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5',
            'strong', 'em',
            'br',
        ]
        self.authorized_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'width', 'height', 'alt'],
            'iframe': ['src', 'width', 'height', 'allowfullscreen']
        }
        if with_media:
            self.authorized_tags += ['img', 'iframe']

    def get_language(self):
        ideascube_language = get_language()
        return _ideascube_to_tinyMCE_language_map.get(
            ideascube_language, ideascube_language)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        # The widget displayed to the user
        div_attrs = {'id': name,
                     'class': 'tinymce-editor',
                     'data-tinymce-use-media': self.with_media,
                     'data-tinymce-language-code': self.get_language()
                    }
        div_html = '<div{}>{}</div>'.format(
            flatatt(div_attrs),
            force_text(value)
        )

        # The input used by django
        input_attrs = self.build_attrs(attrs, name=name, value=escape(value),
                                       type='hidden')
        input_html = '<input{} />'.format(
            flatatt(input_attrs)
        )

        html = '\n'.join([div_html, input_html])
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        raw_html_input = super().value_from_datadict(data, files, name)
        filtered_html = bleach.clean(
            raw_html_input,
            self.authorized_tags,
            self.authorized_attributes)
        return filtered_html


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
