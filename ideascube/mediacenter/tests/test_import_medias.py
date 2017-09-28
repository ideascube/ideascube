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
    metadata = ('kind,title,summary,credits,path,lang\n'
                'video,my video,my video summary,BSF,a-video.mp4,ar\n'
                'pdf,my doc,my doc summary,BSF,a-pdf.pdf,en\n'
                'image,my image,my image summary,BSF,an-image.jpg,es\n'
                'image,no summary,,BSF,an-image.jpg,fr\n'
                'image,no credits,my summary,,an-image.jpg,ku\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 5
    video = Document.objects.get(title='my video')
    assert video.summary == 'my video summary'
    assert video.kind == Document.VIDEO
    assert Document.objects.search('summary').count() == 5
    assert Document.objects.search('BSF').count() == 4


@pytest.mark.parametrize('row', [
    pytest.param('image,,my summary,BSF,an-image.jpg,ar', id='missing-title'),
    pytest.param('image,my title,my summary,BSF,,ar', id='missing-path'),
    pytest.param(
        'image,my title,my summary,BSF,unknownpath.mp4,ar', id='invalid-path'),
    pytest.param(
        'image,my title,my summary,BSF,an-image.jpg,', id='missing-lang'),
])
def test_should_skip_if_missing_required_metadata(row):
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path,lang\n' + row)
    write_metadata(metadata)
    with pytest.raises(SystemExit):
        call_command('import_medias', CSV_PATH)
    assert not Document.objects.count()


def test_should_cut_too_long_title():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path,lang\n'
                'image,This is a very long title with much much more than one hundrer chars so it should be cut to be imported,my summary,BSF,an-image.jpg,ar')  # noqa
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    doc = Document.objects.last()
    assert doc.title.startswith('This is a very long title with')


def test_should_not_reimport_if_already_existing():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path,lang\n'
                'video,my video,my video summary,BSF,a-video.mp4,ar\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    # Call again.
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1


def test_should_update_if_already_existing_and_update_flag_used():
    assert not Document.objects.count()
    metadata = ('kind,title,summary,credits,path,lang\n'
                'video,my video,my video summary,BSF,a-video.mp4,ku\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    metadata = ('kind,title,summary,credits,path,lang\n'
                'video,my video,another summary,BSF,a-video.mp4,ku\n')
    write_metadata(metadata)
    # Call again.
    call_command('import_medias', CSV_PATH, update=True)
    assert Document.objects.count() == 1
    assert Document.objects.last().summary == 'another summary'


def test_should_guess_kind_from_path():
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,lang\n'
                'my video,my video summary,BSF,a-video.mp4,ku\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    video = Document.objects.get(title='my video')
    assert video.kind == Document.VIDEO


def test_long_path():
    assert not Document.objects.count()
    prefix = 'A' * 100
    long_path = prefix + '.mp4'
    long_preview = prefix + 'an-image.jpg'
    metadata = ('title,summary,credits,lang,path,preview\n'
                'my video,my video summary,BSF,ku,'
                + long_path + ',' + long_preview + '\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    video = Document.objects.get(title='my video')
    assert video.kind == Document.VIDEO


def test_should_add_preview_if_given():
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,preview,lang\n'
                'my video,my video summary,BSF,a-video.mp4,an-image.jpg,es\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    assert Document.objects.get(title='my video').preview


def test_should_add_tags_if_given():
    assert not Document.objects.count()
    metadata = ('title;summary;credits;path;tags;lang\n'
                'my video;my video summary;BSF;a-video.mp4;tag1,tag2;es')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 1
    assert Document.objects.get(title='my video', tags__name="tag1")
    assert Document.objects.get(title='my video', tags__name="tag2")


@pytest.mark.parametrize('dry_run', [False, True])
def test_should_fail_nicely_if_path_doesn_t_exist(capsys, dry_run):
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,preview,lang\n'
                'image, summary,BSF,an-image.jpg,not_existing0,ar\n'
                'image, summary,BSF,not_existing1,,es\n'
                'image, summary,BSF,not_existing2,not_existing3,fr\n')
    write_metadata(metadata)
    with pytest.raises(SystemExit):
        call_command('import_medias', CSV_PATH, dry_run=dry_run)
    assert not Document.objects.count()
    out, _ = capsys.readouterr()
    for i in range(4):
        assert "not_existing{}".format(i) in out


@pytest.mark.parametrize('dry_run', [False, True])
def test_should_fail_nicely_if_path_is_a_dir(capsys, dry_run):
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,preview,lang\n'
                'image, summary,BSF,an-image.jpg,a-directory,ar\n'
                'image, summary,BSF,a-directory,,es\n'
                'image, summary,BSF,a-directory,a-directory,fr\n')
    write_metadata(metadata)
    with pytest.raises(SystemExit):
        call_command('import_medias', CSV_PATH, dry_run=dry_run)
    assert not Document.objects.count()
    out, _ = capsys.readouterr()
    assert out.count("a-directory") == 4


def test_import_media_allow_subdir():
    assert not Document.objects.count()
    metadata = ('title,summary,credits,path,preview,lang\n'
                'video,summary,BSF,subdir/a-video.mp4,subdir/an-image.jpg,ar\n'
                'pdf,summary,BSF,subdir/a-pdf.pdf,subdir/an-image.jpg,es\n')
    write_metadata(metadata)
    call_command('import_medias', CSV_PATH)
    assert Document.objects.count() == 2
    for document in Document.objects.all():
        assert os.path.dirname(document.original.path).endswith('/subdir')
        assert os.path.dirname(document.preview.path).endswith('/subdir')
