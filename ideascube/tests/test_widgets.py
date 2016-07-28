import pytest


@pytest.mark.usefixtures('db')
def test_filtered_lang_select():
    from ideascube.widgets import LangSelect

    expected = (
        '<option value="fr">Français (fr)</option>\n'
        '<option value="en">English (en)</option>'
        )

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render_options([], [])
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_local_setting(user):
    from ideascube.models import Setting
    from ideascube.widgets import LangSelect

    Setting.set('content', 'local-languages', ['en', 'zh-hant'], user)
    expected = (
        '<option value="en">English (en)</option>\n'
        '<option value="zh-hant">繁體中文 (zh-hant)</option>'
        )

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render_options([], [])
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_pre_selected(user):
    from ideascube.models import Setting
    from ideascube.widgets import LangSelect

    Setting.set('content', 'local-languages', ['en', 'zh-hant'], user)
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
    rendered = widget.render_options([], ['fr'])
    assert rendered == expected
