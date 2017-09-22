import pytest

from ..utils import guess_kind_from_filename, guess_kind_from_content_type


@pytest.mark.parametrize('input,expected', [
    ['pouet.jpg', 'image'],
    ['pouet.jpeg', 'image'],
    ['pouet.png', 'image'],
    ['pouet.mp4', 'video'],
    ['pouet.avi', 'video'],
    ['pouet.mp3', 'audio'],
    ['pouet.ogg', 'audio'],
    ['pouet.pdf', 'pdf'],
    ['pouet.epub', 'epub'],
    ['pouet.exe', 'app'],
    ['pouet.mobi', 'mobi'],
    ['pouet', None],
    ['pouet.xxx', None],
])
def test_guess_kind_from_filename(input, expected):
    assert guess_kind_from_filename(input) == expected


@pytest.mark.parametrize('input,expected', [
    ['image/jpg', 'image'],
    ['image/jpeg', 'image'],
    ['image/png', 'image'],
    ['video/mp4', 'video'],
    ['video/avi', 'video'],
    ['audio/mpeg', 'audio'],
    ['audio/ogg', 'audio'],
    ['application/pdf', 'pdf'],
    ['', None],
    [None, None],
])
def test_guess_kind_from_content_type(input, expected):
    assert guess_kind_from_content_type(input) == expected
