import pytest

from ..templatetags.mediacenter_tags import htmlize_description



def test_do_not_change_no_special_text():
    input = "A text without particular change to apply on."
    output = htmlize_description(input)
    assert output == input


def test_change_http_link():
    input = "A text with a link http://foo.bar?q=stuff&r=bar"
    output = htmlize_description(input)
    assert output == 'A text with a link <a href="http://foo.bar?q=stuff&r=bar">http://foo.bar?q=stuff&r=bar</a>'


def test_change_https_link():
    input = "A text with a link https://foo.bar?q=stuff&r=bar"
    output = htmlize_description(input)
    assert output == 'A text with a link <a href="https://foo.bar?q=stuff&r=bar">https://foo.bar?q=stuff&r=bar</a>'


def test_change_new_lines():
    input = ('A text with\n'
             'several lines\r\n'
             'and several\r'
             'new line types.\n\n\n'
             'Even with several new line\r\r\n\n'
             'in a row')
    output = htmlize_description(input)
    assert output == ('A text with<br/>'
                      'several lines<br/>'
                      'and several<br/>'
                      'new line types.<br/><br/><br/>'
                      'Even with several new line<br/><br/><br/>'
                      'in a row')


def test_all_together():
    input = ('A text with\n'
             'several links http://foo.bar https://me.fr\r\n'
             'mixed with several\r'
             'new line types.')
    output = htmlize_description(input)
    assert output == ('A text with<br/>'
                      'several links <a href="http://foo.bar">http://foo.bar</a> <a href="https://me.fr">https://me.fr</a><br/>'
                      'mixed with several<br/>'
                      'new line types.')


@pytest.mark.skip(reason="That's become a bit to complex, do we need to handle it")
def test_escape_html_link():
    # original (unescaped html) input = '<a href="http:/you.com">you</a>'
    input = '&lt;a href=&quot;http://you.com&quot;&gt;you&lt;/a&gt;'
    output = htmlize_description(input)
    assert output == '&lt;a href=&quot;<a href="http://you.com">http://you.com</a>&quot;&gt;you&lt;/a&gt;'