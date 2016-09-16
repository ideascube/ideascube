from django.core.management import call_command

import pytest

from ideascube.mediacenter.tests.factories import DocumentFactory
from taggit.models import Tag

pytestmark = pytest.mark.django_db


def test_count_should_count_usage(capsys):
    DocumentFactory.create_batch(size=4, tags=['tag1'])
    call_command('tags', 'count', 'tag1')
    out, err = capsys.readouterr()
    assert '4 object(s)' in out


def test_rename_should_rename_tag():
    doc = DocumentFactory(tags=['tag1'])
    tag1 = Tag.objects.get(name='tag1')
    call_command('tags', 'rename', 'tag1', 'tag2')
    assert not Tag.objects.filter(name='tag1')
    assert 'tag2' in doc.tags.names()
    assert 'tag1' not in doc.tags.names()
    assert tag1.id == Tag.objects.get(name='tag2').id


def test_rename_should_exit_on_non_existing_tag():
    DocumentFactory(tags=['tag1'])
    with pytest.raises(SystemExit):
        call_command('tags', 'rename', 'tag3', 'tag2')
    assert Tag.objects.filter(name='tag1')


def test_rename_should_exit_if_new_name_already_exists():
    DocumentFactory(tags=['tag1'])
    Tag.objects.create(name='tag2')
    with pytest.raises(SystemExit):
        call_command('tags', 'rename', 'tag1', 'tag2')
    assert Tag.objects.filter(name='tag1')
    assert Tag.objects.filter(name='tag2')


def test_replace_should_replace_and_delete_tag():
    tag1 = Tag.objects.create(name='tag1')
    tag2 = Tag.objects.create(name='tag2')
    doc = DocumentFactory(tags=[tag1])
    call_command('tags', 'replace', 'tag1', 'tag2')
    assert not Tag.objects.filter(name='tag1')
    assert tag1 not in doc.tags.all()
    assert tag2 in doc.tags.all()
    assert tag1.id != tag2.id


def test_replace_should_create_if_needed():
    doc = DocumentFactory(tags=['tag1'])
    call_command('tags', 'replace', 'tag1', 'tag2')
    tag2 = Tag.objects.get(name='tag2')
    assert not Tag.objects.filter(name='tag1')
    assert 'tag1' not in doc.tags.names()
    assert tag2 in doc.tags.all()


def test_delete_should_delete_tag():
    tag1 = Tag.objects.create(name='tag1')
    call_command('tags', 'delete', 'tag1')
    assert not Tag.objects.filter(name='tag1')
    assert not Tag.objects.filter(pk=tag1.pk)


def test_delete_should_exit_on_non_existing_tag():
    with pytest.raises(SystemExit):
        call_command('tags', 'delete', 'tag1')


def test_list_should_list_tags_and_slugs(capsys):
    tag = Tag.objects.create(name='Some Tag')
    call_command('tags', 'list',)
    out, err = capsys.readouterr()
    assert tag.name in out
    assert tag.slug in out
