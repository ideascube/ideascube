import pytest

from ideascube.widgets import LangSelect
from ideascube.configuration import set_config


@pytest.mark.usefixtures('db')
def test_filtered_lang_select():
    # Note: this depends on the default value for content.local-languages
    expected = (
        '<option value="fr">Français (fr)</option>\n'
        '<option value="en">English (en)</option>'
        )

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render_options([])
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_local_setting(user):
    set_config('content', 'local-languages', ['en', 'zh-hant'], user)
    expected = (
        '<option value="en">English (en)</option>\n'
        '<option value="zh-hant">繁體中文 (zh-hant)</option>'
        )

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render_options([])
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_pre_selected(user):
    set_config('content', 'local-languages', ['en', 'zh-hant'], user)
    expected = (
        '<option value="fr" selected="selected">Français (fr)</option>\n'
        '<option value="en">English (en)</option>\n'
        '<option value="zh-hant">繁體中文 (zh-hant)</option>'
        )

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render_options(['fr'])
    assert rendered == expected
