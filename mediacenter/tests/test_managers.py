import pytest

from ..models import Document

pytestmark = pytest.mark.django_db


def test_video_should_return_only_video(video, image, audio):
    contents = Document.objects.video()
    assert video in contents
    assert image not in contents
    assert audio not in contents


def test_image_should_return_only_image(video, image, audio):
    contents = Document.objects.image()
    assert video not in contents
    assert image in contents
    assert audio not in contents


def test_audio_should_return_only_audio(video, image, audio):
    contents = Document.objects.audio()
    assert video not in contents
    assert image not in contents
    assert audio in contents


def test_pdf_should_return_only_pdf(video, image, pdf):
    contents = Document.objects.pdf()
    assert video not in contents
    assert image not in contents
    assert pdf in contents


def test_text_should_return_only_pdf(video, image, text):
    contents = Document.objects.text()
    assert video not in contents
    assert image not in contents
    assert text in contents


def test_objects_should_return_all_content(video, image, audio):
    contents = Document.objects.all()
    assert video in contents
    assert image in contents
    assert audio in contents
