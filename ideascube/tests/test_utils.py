from io import BytesIO

import pytest

from ideascube.utils import to_unicode, get_file_sha256, tag_splitter, MetaRegistry
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


@pytest.mark.parametrize('string', [
    'foo,bar,stuff:fuzzy',
    'foo, bar, stuff:fuzzy',
    'bar, stuff:fuzzy; foo',
    ';;;; bar,   *stuff:fuzzy---,foo  ',
])
def test_tag_splitter_simple_tags(string):
    oracle = set(['foo', 'bar', 'stuff:fuzzy'])
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

def test_different_cases_make_same_tags():
    oracle = set(['bar'])
    tags = tag_splitter("bar, Bar, BAR, baR")
    assert len(tags) == len(oracle)
    assert set(tags) == oracle


def test_meta_registry_one_base():
    # Ensure the base type itself is not added to the registry
    class Base1(metaclass=MetaRegistry):
        pass

    assert Base1 not in Base1.registered_types.values()

    # Register a new type, make sure it gets added to the registry
    class Child1(Base1):
        pass

    assert Base1.registered_types['Child1'] == Child1

    # Register a new type with a specific name,
    # make sure it gets added to the registry
    class Child2(Base1, typename='foo'):
        pass

    assert Base1.registered_types['foo'] == Child2
    assert 'Child2' not in Base1.registered_types

    # Define a new type discarding registration, make sure it
    # does **not** get added to the registry
    class NotRegistered(Base1, no_register=True):
        pass

    assert NotRegistered not in Base1.registered_types.values()


def test_meta_registry_two_base():
    # Ensure the base type itself is not added to the registry
    class Base1(metaclass=MetaRegistry):
        pass

    class Base2(metaclass=MetaRegistry):
        pass

    assert Base1 not in Base1.registered_types.values()
    assert Base2 not in Base1.registered_types.values()
    assert Base1 not in Base2.registered_types.values()
    assert Base2 not in Base2.registered_types.values()

    # Register a new type, make sure it gets added to the registry
    class Child1(Base1):
        pass

    assert Base1.registered_types['Child1'] == Child1
    assert Child1 not in Base2.registered_types.values()


def test_rm_file(tmpdir):
    from ideascube.utils import rm

    path = tmpdir.join('to-remove')
    path.write_text('REMOVE ME!', 'utf-8')
    assert path.check(file=True)

    rm(path.strpath)
    assert path.check(exists=False)


def test_rm_tree(tmpdir):
    from ideascube.utils import rm

    dirpath = tmpdir.mkdir('to-remove')
    subdirpath = dirpath.mkdir('subdir')
    subfilepath = subdirpath.join('file')
    subfilepath.write_text('REMOVE ME!', 'utf-8')
    assert subfilepath.check(file=True)

    rm(dirpath.strpath)
    assert dirpath.check(exists=False)


def test_rm_inexistent_file(tmpdir):
    from ideascube.utils import rm

    path = tmpdir.join('does-not-exist')
    assert path.check(exists=False)

    rm(path.strpath)
    assert path.check(exists=False)
