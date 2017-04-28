import pytest

from ideascube.widgets import LangSelect, RichTextEntry
from ideascube.configuration import set_config


@pytest.mark.usefixtures('db')
def test_filtered_lang_select():
    # Note: this depends on the default value for content.local-languages
    expected = '\n'.join([
        '<select name="lang-test">',
        '  <option value="fr">Français (fr)</option>\n',
        '  <option value="en">English (en)</option>\n',
        '</select>',
    ])

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render('lang-test', None)
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_local_setting(user):
    set_config('content', 'local-languages', ['en', 'zh-hant'], user)
    expected = '\n'.join([
        '<select name="lang-test">',
        '  <option value="en">English (en)</option>\n',
        '  <option value="zh-hant">繁體中文 (zh-hant)</option>\n',
        '</select>',
    ])

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render('lang-test', None)
    assert rendered == expected


@pytest.mark.usefixtures('db')
def test_filtered_lang_select_with_pre_selected(user):
    set_config('content', 'local-languages', ['en', 'zh-hant'], user)
    expected = '\n'.join([
        '<select name="lang-test">',
        '  <option value="fr" selected>Français (fr)</option>\n',
        '  <option value="en">English (en)</option>\n',
        '  <option value="zh-hant">繁體中文 (zh-hant)</option>\n',
        '</select>',
    ])

    widget = LangSelect(choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('zh-hant', '繁體中文'),
        ])
    rendered = widget.render('lang-test', 'fr')
    assert rendered == expected


def test_richtext_entry():
    rte = RichTextEntry()

    rendered_rte = rte.render('richtextentry', None)
    assert rendered_rte == '\n'.join([
        '<div class="tinymce-editor" data-tinymce-language-code="en" id="richtextentry"></div>',
        ('<input name="richtextentry" type="hidden"'
         ' value="" />')
    ])


def test_richtext_entry_with_content():
    rte = RichTextEntry()

    rendered_rte = rte.render('richtextentry', "<p>A text</p>")
    assert rendered_rte == '\n'.join([
        '<div class="tinymce-editor" data-tinymce-language-code="en" id="richtextentry"><p>A text</p></div>',
        ('<input name="richtextentry" type="hidden"'
         ' value="&lt;p&gt;A text&lt;/p&gt;" />')
    ])


def test_richtext_entry_with_media():
    rte = RichTextEntry(with_media=True)

    rendered_rte = rte.render('richtextentry', None)
    assert rendered_rte == '\n'.join([
        '<div class="tinymce-editor" data-tinymce-language-code="en" id="richtextentry" data-tinymce-use-media></div>',
        ('<input name="richtextentry" type="hidden"'
         ' value="" />')
    ])
