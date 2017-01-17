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


def test_combobox_entry():
    from ideascube.widgets import ComboBoxEntry

    choices = (
        ('foo', 'Foo'), ('bar', 'Bar'),
    )
    cbe = ComboBoxEntry(choices)
    assert cbe._choices == choices

    assert cbe.decompress('foo') == ['foo', 'Foo']
    assert cbe.decompress('bar') == ['bar', 'Bar']
    assert cbe.decompress('baz') == [None, None]
    assert cbe.decompress(None) == [None, None]

    datadict = {
       'cbe_0': 'foo', 'cbe_1': 'Foo',
       'cbf_0': 'Baz', 'cbf_1': 'Baz',
    }
    assert cbe.value_from_datadict(datadict, {}, 'cbe') == 'foo'
    assert cbe.value_from_datadict(datadict, {}, 'cbf') == 'Baz'
    assert cbe.value_from_datadict(datadict, {}, 'cbg') == ''

    assert cbe.render('cbe', None) == '\n'.join([
        '<div class="comboboxentry">',
        '<input autocomplete="off" name="cbe_0" type="hidden" />',
        ('<input autocomplete="off" name="cbe_1" type="text" />'
         '<button class="button" type="button">▾</button>'),
        '<ul>',
        '<li data-value="foo">Foo</li>',
        '<li data-value="bar">Bar</li>',
        '</ul>',
        '</div>'])
    assert cbe.render('cbe', '') == '\n'.join([
        '<div class="comboboxentry">',
        '<input autocomplete="off" name="cbe_0" type="hidden" />',
        ('<input autocomplete="off" name="cbe_1" type="text" />'
         '<button class="button" type="button">▾</button>'),
        '<ul>',
        '<li data-value="foo">Foo</li>',
        '<li data-value="bar">Bar</li>',
        '</ul>',
        '</div>'])
    assert cbe.render('cbe', 'foo') == '\n'.join([
        '<div class="comboboxentry">',
        '<input autocomplete="off" name="cbe_0" type="hidden" value="foo" />',
        ('<input autocomplete="off" name="cbe_1" type="text" value="Foo" />'
         '<button class="button" type="button">▾</button>'),
        '<ul>',
        '<li data-value="foo">Foo</li>',
        '<li data-value="bar">Bar</li>',
        '</ul>',
        '</div>'])
    assert cbe.render('cbe', 'Baz') == '\n'.join([
        '<div class="comboboxentry">',
        '<input autocomplete="off" name="cbe_0" type="hidden" />',
        ('<input autocomplete="off" name="cbe_1" type="text" />'
         '<button class="button" type="button">▾</button>'),
        '<ul>',
        '<li data-value="foo">Foo</li>',
        '<li data-value="bar">Bar</li>',
        '</ul>',
        '</div>'])


def test_comboboxentry_blank():
    from ideascube.widgets import ComboBoxEntry

    choices = (
        ('foo', 'Foo'), ('bar', 'Bar'),
    )
    cbe = ComboBoxEntry(choices, blank=True)
    assert cbe._choices[0] == ('', '---------')
    assert cbe._choices[1:] == choices

    assert cbe.render('cbe', None) == '\n'.join([
        '<div class="comboboxentry">',
        '<input autocomplete="off" name="cbe_0" type="hidden" />',
        ('<input autocomplete="off" name="cbe_1" type="text" />'
         '<button class="button" type="button">▾</button>'),
        '<ul>',
        '<li data-value="">---------</li>',
        '<li data-value="foo">Foo</li>',
        '<li data-value="bar">Bar</li>',
        '</ul>',
        '</div>'])
