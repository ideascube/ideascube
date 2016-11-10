from io import BytesIO

import pytest


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
