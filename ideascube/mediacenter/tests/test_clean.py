import io
import os, stat
import pytest

from django.core.management import call_command
from django.core.files import File

from ideascube.mediacenter.models import Document
from .factories import DocumentFactory

pytestmark = pytest.mark.django_db

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


def test_clean_leftover_should_not_fail_if_no_media_or_file():
    call_command('clean', 'leftover-files')


def test_clean_leftover_should_not_remove_files_associated_with_documents(settings):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    original_path = document.original.path
    preview_path = document.preview.path
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)
    call_command('clean', 'leftover-files')
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)


def test_clean_leftover_should_not_remove_files_associated_with_documents_without_preview(settings):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview=None)
    original_path = document.original.path
    assert os.path.exists(original_path)
    call_command('clean', 'leftover-files')
    assert os.path.exists(original_path)


def test_clean_leftover_should_correctly_remove_orphan_files(settings):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    original_path = document.original.path
    preview_path = document.preview.path
    Document.objects.all().delete()
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)
    call_command('clean', 'leftover-files')
    assert not os.path.exists(original_path)
    assert not os.path.exists(preview_path)


def test_clean_leftover_should_fail_nicely_if_cannot_remove(settings, capsys):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    original_path = document.original.path
    preview_path = document.preview.path
    document.delete()
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)
    os.chmod(os.path.join(settings.MEDIA_ROOT, 'mediacenter/document'), stat.S_IRUSR | stat.S_IXUSR)
    call_command('clean', 'leftover-files')
    assert os.path.exists(original_path)
    assert not os.path.exists(preview_path)
    _, err = capsys.readouterr()
    assert "ERROR while deleting {}".format(original_path) in err


def test_clean_leftover_should_not_remove_orphan_files_if_dry_run(settings, capsys):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    original_path = document.original.path
    preview_path = document.preview.path
    Document.objects.all().delete()
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)
    call_command('clean', 'leftover-files', dry_run=True)
    assert os.path.exists(original_path)
    assert os.path.exists(preview_path)
    out, _ = capsys.readouterr()
    assert original_path in out
    assert preview_path in out


def test_clean_leftover_should_correctly_clean_after_document_update(settings):
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    old_original_path = document.original.path
    preview_path = document.preview.path
    with open(os.path.join(DATA_PATH, 'a-pdf.pdf'), 'rb') as f:
        document.original = File(f, name='a-pdf.pdf')
        document.save()
    new_original_path = document.original.path
    assert os.path.exists(old_original_path)
    assert os.path.exists(new_original_path)
    assert os.path.exists(preview_path)
    call_command('clean', 'leftover-files')
    assert not os.path.exists(old_original_path)
    assert os.path.exists(new_original_path)
    assert os.path.exists(preview_path)


def test_clean_leftover_should_correctly_clean_after_complex_situation(settings):
    document0 = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                                preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    document1 = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                                preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    document2 = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                                preview=None)
    document3 = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                                preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))

    file_that_should_be_deleted = [
        document1.original.path,
        document1.preview.path,
        document3.original.path,
        document3.preview.path
    ]
    document1.delete()
    with open(os.path.join(DATA_PATH, 'a-pdf.pdf'), 'rb') as f:
        document3.original = File(f, name='a-pdf.pdf')
        document3.save()
    with open(os.path.join(DATA_PATH, 'an-image.jpg'), 'rb') as f:
        document3.preview = File(f, name='an-image2.jpg')
        document3.save()

    files_that_should_be_kept = [
        document0.original.path,
        document0.preview.path,
        document2.original.path,
        document3.original.path,
        document3.preview.path
    ]

    call_command('clean', 'leftover-files')
    for path in file_that_should_be_deleted:
        assert not os.path.exists(path)
    for path in files_that_should_be_kept:
        assert os.path.exists(path)


def test_clean_media_should_delete_all_media():
    DocumentFactory.create_batch(size=4)
    assert Document.objects.all().count() == 4
    call_command('clean', 'media')
    assert Document.objects.all().count() == 0


def test_clean_media_does_not_do_anything_with_dryrun():
    out = io.StringIO()

    DocumentFactory.create_batch(size=4)
    assert Document.objects.all().count() == 4
    call_command('clean', 'media', '--dry-run', stdout=out)
    assert Document.objects.all().count() == 4
    assert out.getvalue().strip() == '\n'.join([
        '4 documents would have been deleted:',
        '- Test document 17 (other)',
        '- Test document 16 (other)',
        '- Test document 15 (other)',
        '- Test document 14 (other)',
    ])


def test_clean_media_should_delete_leftover_files():
    document = DocumentFactory(original__from_path=os.path.join(DATA_PATH, 'a-video.mp4'),
                               preview__from_path=os.path.join(DATA_PATH, 'an-image.jpg'))
    files_to_delete = [document.original.path, document.preview.path]
    call_command('clean', 'media')
    for path in files_to_delete:
        assert not os.path.exists(path)


def test_clean_media_should_not_delete_media_from_packages(capsys):
    DocumentFactory.create_batch(size=4)
    DocumentFactory.create_batch(size=4, package_id='1')
    assert Document.objects.all().count() == 8
    call_command('clean', 'media')
    assert Document.objects.all().count() == 4
    for document in Document.objects.all():
        assert document.package_id == '1'
    out, _ = capsys.readouterr()
    assert out == """4 documents have been deleted.\n
4 media have been installed by packages and have not been deleted.
Remove the corresponding package(s) if you want to delete them with the command:
catalog remove pkgid+
"""


def test_clean_media_by_type():
    DocumentFactory.create_batch(size=2, kind=Document.AUDIO)
    DocumentFactory.create_batch(size=2, kind=Document.VIDEO)
    DocumentFactory.create_batch(size=2, kind=Document.OTHER)
    DocumentFactory.create_batch(size=2, kind=Document.TEXT)
    assert Document.objects.all().count() == 8

    call_command('clean', 'media', '--type=other')
    assert Document.objects.all().count() == 6
    assert Document.objects.filter(kind=Document.OTHER).count() == 0

    call_command('clean', 'media', '--type=audio', '--type=video')
    assert Document.objects.all().count() == 2
    assert Document.objects.filter(kind=Document.AUDIO).count() == 0
    assert Document.objects.filter(kind=Document.VIDEO).count() == 0
