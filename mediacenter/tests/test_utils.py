import pytest

from ..utils import guess_kind


@pytest.mark.parametrize('input,expected', [
    ['pouet.jpg', 'image'],
    ['pouet.jpeg', 'image'],
    ['pouet.png', 'image'],
    ['pouet.mp4', 'video'],
    ['pouet.avi', 'video'],
    ['pouet.mp3', 'audio'],
    ['pouet.ogg', 'audio'],
    ['pouet.pdf', 'pdf'],
    ['pouet', None],
    ['pouet.xxx', None],
])
def test_guess_kind(input, expected):
    assert guess_kind(input) == expected
