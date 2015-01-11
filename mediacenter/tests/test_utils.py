import pytest

from ..utils import guess_type


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
])
def test_guess_type(input, expected):
    assert guess_type(input) == expected
