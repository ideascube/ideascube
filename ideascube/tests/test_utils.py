from io import BytesIO

import pytest

from ideascube.utils import to_unicode, get_file_sha256, get_file_size, tag_splitter
from hashlib import sha256


@pytest.mark.parametrize(
    'input, expected, encoding',
    [
        ('abcd\néfgh', ['abcd\n', 'éfgh'], 'latin-1'),
        ('abcd\néfgh', ['abcd\n', 'éfgh'], 'utf-8'),
        ('abcd\r\néfgh', ['abcd\n', 'éfgh'], 'latin-1'),
        ('abcd\r\néfgh', ['abcd\n', 'éfgh'], 'utf-8'),
    ],
    ids=['latin1', 'utf8', 'windows-latin1', 'windows-utf8'],
)
def test_textio_wrapper(input, expected, encoding):
    from ideascube.utils import TextIOWrapper

    input = input.encode(encoding)
    stream = BytesIO(input)

    # Try with an explicit encoding, it should behave like TextIOWrapper
    for i, line in enumerate(TextIOWrapper(stream, encoding=encoding)):
        assert line == expected[i]

    stream = BytesIO(input)

    # Now try letting it guess the encoding
    for i, line in enumerate(TextIOWrapper(stream)):
        assert line == expected[i]


@pytest.mark.parametrize('string', [
    u'éééé'.encode('latin-1'),
    u'éééé'
])
def test_to_unicode(string):
    assert isinstance(to_unicode(string), str)


def test_sha256(tmpdir):
    file_path = tmpdir.join("file")
    content = b"abcdefghijklmnopqrstuvw"
    with file_path.open("wb") as f:
        f.write(content)
    assert get_file_sha256(str(file_path)) == sha256(content).hexdigest()


def test_size(tmpdir):
    file_path = tmpdir.join("file")
    content = b"abcdefghijklmnopqrstuvw"
    with file_path.open("wb") as f:
        f.write(content)
    assert get_file_size(str(file_path)) == len(content)


@pytest.mark.parametrize('string', [
    'foo,bar,stuff,fuzzy',
    'foo, bar, stuff, fuzzy',
    'bar, stuff; fuzzy, foo',
    ';;;; bar,   stuff    ;,fuzzy,foo  '
])
def test_tag_splitter_simple_tags(string):
    oracle = set(['foo', 'bar', 'stuff', 'fuzzy'])
    tags = tag_splitter(string)
    assert len(tags) == len(oracle)
    assert set(tags) == oracle


@pytest.mark.parametrize('string', [
    'black & white,stuff,fuzzy',
    'black & white;fuzzy;stuff',
    ';stuff; black & white,stuff,fuzzy',
    '    black & white   ,,,, stuff  ,fuzzy',
])
def test_tag_splitter_tags_with_spaces(string):
    oracle = set(['black & white', 'stuff', 'fuzzy'])
    tags = tag_splitter(string)
    assert len(tags) == len(oracle)
    assert set(tags) == oracle

def test_different_cases_make_different_tags():
    oracle = set(['bar', 'Bar', 'BAR', 'baR'])
    tags = tag_splitter("bar, Bar, BAR, baR")
    assert len(tags) == len(oracle)
    assert set(tags) == oracle
