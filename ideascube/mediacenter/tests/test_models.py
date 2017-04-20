import pytest

from .factories import DocumentFactory

import os.path
import stat

@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_delete_file_also():
    from django.conf import settings
    file_name = 'foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'w'): pass
    document = DocumentFactory(original=file_name)
    document.delete()
    assert not os.path.exists(file_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_delete_preview_also():
    from django.conf import settings
    file_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'w'): pass
    document = DocumentFactory(preview=file_name)
    document.delete()
    assert not os.path.exists(file_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_delete_file_and_preview_also():
    from django.conf import settings
    file_name = 'foo.img'
    preview_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'w'): pass
    preview_path = os.path.join(settings.MEDIA_ROOT, preview_name)
    with open(preview_path, 'w'): pass
    document = DocumentFactory(original=file_name, preview=preview_name)
    document.delete()
    assert not os.path.exists(file_path)
    assert not os.path.exists(preview_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_not_fail_if_file_already_deleted():
    from django.conf import settings
    file_name = 'foo.img'
    preview_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    preview_path = os.path.join(settings.MEDIA_ROOT, preview_name)
    with open(preview_path, 'w'): pass
    document = DocumentFactory(original=file_name, preview=preview_name)
    document.delete()
    assert not os.path.exists(file_path)
    assert not os.path.exists(preview_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_not_fail_if_preview_already_deleted():
    from django.conf import settings
    file_name = 'foo.img'
    preview_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'w'): pass
    preview_path = os.path.join(settings.MEDIA_ROOT, preview_name)
    document = DocumentFactory(original=file_name, preview=preview_name)
    document.delete()
    assert not os.path.exists(file_path)
    assert not os.path.exists(preview_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_not_fail_if_file_and_preview_already_deleted():
    from django.conf import settings
    file_name = 'foo.img'
    preview_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    preview_path = os.path.join(settings.MEDIA_ROOT, preview_name)
    document = DocumentFactory(original=file_name, preview=preview_name)
    document.delete()
    assert not os.path.exists(file_path)
    assert not os.path.exists(preview_path)


@pytest.mark.django_db(transaction=True)
def test_deleting_document_should_not_fail_if_deletion_is_impossible(capsys):
    from django.conf import settings
    file_name = 'foo.img'
    preview_name = 'preview_foo.img'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'w'): pass
    preview_path = os.path.join(settings.MEDIA_ROOT, preview_name)
    with open(preview_path, 'w'): pass
    os.chmod(settings.MEDIA_ROOT, stat.S_IRUSR | stat.S_IXUSR)
    document = DocumentFactory(original=file_name, preview=preview_name)
    document.delete()
    assert os.path.exists(file_path)
    assert os.path.exists(preview_path)
    _, err = capsys.readouterr()
    assert "ERROR while deleting {}".format(file_path) in err
    assert "ERROR while deleting {}".format(preview_path) in err

