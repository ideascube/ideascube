import os

from django.core.management import call_command

import pytest

from ideascube.mediacenter.models import Document

pytestmark = pytest.mark.django_db
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data/metadata.csv')


def write_metadata(metadata):
    with open(CSV_PATH, 'w') as f:
        f.write(metadata)


def teardown_function(function):
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)


def test_should_import_medias():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf\n'
                'image,my image,my image summary,BSF,an-image.jpg\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 3
    video = Document.objects.get(title='my video')
    assert video.summary == 'my video summary'
    assert video.kind == Document.VIDEO


@pytest.mark.parametrize('row', [
    'image,,my summary,BSF,an-image.jpg',
    'image,my title,,BSF,an-image.jpg',
    'image,my title,my summary,,an-image.jpg',
    'image,my title,my summary,BSF,',
    'image,my title,my summary,BSF,unknownpath.mp4',
])
def test_should_skip_if_missing_required_metadata(row):
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path\n' + row)
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert not Document.objects.count()


def test_should_cut_too_long_title():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path\n'
                'image,This is a very long title with much much more than one hundrer chars so it should be cut to be imported,my summary,BSF,an-image.jpg')  # noqa
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    doc = Document.objects.last()
    assert doc.title.startswith('This is a very long title with')


def test_should_not_reimport_if_already_existing():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    # Call again.
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1


def test_should_update_if_already_existing_and_update_flag_used():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,my video summary,BSF,a-video.mp4\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    metadata = ('kind,title,summary,credits,path\n'
                'video,my video,another summary,BSF,a-video.mp4\n')
    write_metadata(metadata)
    # Call again.
    call_command('import_medias', CSV_PATH, update=True)
    assert Document.objects.count() == 1
    assert Document.objects.last().summary == 'another summary'


def test_should_guess_kind_from_path():
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path\n'
                'my video,my video summary,BSF,a-video.mp4\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    video = Document.objects.get(title='my video')
    assert video.kind == Document.VIDEO


def test_should_add_preview_if_given():
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,preview\n'
                'my video,my video summary,BSF,a-video.mp4,an-image.jpg\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    assert Document.objects.get(title='my video').preview


def test_should_add_tags_if_given():
    assert not Document.objects.count()
    metadata = ('title;summary;credits;path;tags\n'
                'my video;my video summary;BSF;a-video.mp4;tag1,tag2')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    assert Document.objects.get(title='my video', tags__name="tag1")
    assert Document.objects.get(title='my video', tags__name="tag2")


def test_should_honour_lang_if_given(settings):
    settings.LANGUAGE_CODE = 'fr'
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,lang\n'
                'my video,my video summary,BSF,a-video.mp4,ar\n'
                'my image,my image summary,BSF,an-image.jpg,')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 2
    assert Document.objects.get(title='my image').lang == 'fr'
    assert Document.objects.get(title='my video').lang == 'ar'
