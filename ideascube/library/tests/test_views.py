import zipfile
from datetime import datetime

import pytest
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from webtest import Upload

from ..models import Book, BookSpecimen
from ..views import BookExport, BookSpecimenExport, Index
from .factories import (BookFactory, BookSpecimenFactory,
                        DigitalBookSpecimenFactory)

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app):
    assert app.get(reverse('library:index'), status=200)


def test_only_books_with_specimen_should_be_in_index(app, book, specimen):
    response = app.get(reverse('library:index'))
    assert specimen.item.name in response.content.decode()
    assert book.name not in response.content.decode()


def test_all_books_should_be_in_index_for_staff(staffapp, book, specimen):
    response = staffapp.get(reverse('library:index'))
    assert specimen.item.name in response.content.decode()
    assert book.name in response.content.decode()


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    BookSpecimenFactory.create_batch(size=4)
    url = reverse('library:index')
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get('{url}?page=2'.format(url=url))
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get('{url}?page=3'.format(url=url), status=404)


def test_books_are_ordered_by_created_at_by_default(app):
    book3 = BookFactory()
    book1 = BookFactory()
    book2 = BookFactory()
    BookSpecimenFactory(item=book1)
    BookSpecimenFactory(item=book2)
    BookSpecimenFactory(item=book3)
    # Update without calling save (which would not honour created_at).
    Book.objects.filter(pk=book1.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 17))
    Book.objects.filter(pk=book2.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 16))
    Book.objects.filter(pk=book3.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 15))
    response = app.get(reverse('library:index'))
    titles = response.pyquery.find('.book-list h3')
    assert book1.name in titles[0].text_content()
    assert book2.name in titles[1].text_content()
    assert book3.name in titles[2].text_content()


def test_should_take_sort_parameter_into_account(app):
    book3 = BookFactory()
    book1 = BookFactory()
    book2 = BookFactory()
    BookSpecimenFactory(item=book1)
    BookSpecimenFactory(item=book2)
    BookSpecimenFactory(item=book3)
    # Update without calling save (which would not honour created_at).
    Book.objects.filter(pk=book1.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 17))
    Book.objects.filter(pk=book2.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 16))
    Book.objects.filter(pk=book3.pk).update(created_at=datetime(2016, 6,
                                            26, 16, 15))
    response = app.get(reverse('library:index'), {'sort': 'asc'})
    titles = response.pyquery.find('.book-list h3')
    assert book3.name in titles[0].text_content()
    assert book2.name in titles[1].text_content()
    assert book1.name in titles[2].text_content()


def test_should_take_order_by_parameter_into_account(app):
    book3 = BookFactory(authors='Corneille')
    book1 = BookFactory(authors='Antoine de Saint-Exupéry')
    book2 = BookFactory(authors='Blaise Pascal')
    BookSpecimenFactory(item=book1)
    BookSpecimenFactory(item=book2)
    BookSpecimenFactory(item=book3)
    response = app.get(reverse('library:index'), {'sort': 'asc',
                                                  'order_by': 'authors'})
    titles = response.pyquery.find('.book-list h3')
    assert book1.name in titles[0].text_content()
    assert book2.name in titles[1].text_content()
    assert book3.name in titles[2].text_content()


def test_everyone_should_access_book_detail_page(app, book):
    assert app.get(reverse('library:book_detail',
                           kwargs={'pk': book.pk}), status=200)


def test_book_detail_page_does_not_list_specimens_to_non_staff(app, book):
    specimen = BookSpecimenFactory(item=book, barcode='123789')
    DigitalBookSpecimenFactory(item=book, file__filename='book.epub')
    resp = app.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain(no=[specimen.barcode])


def test_book_detail_page_shows_warning_message_to_staff_if_no_specimens(staffapp, book):
    resp = staffapp.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain("Please add a specimen, or the book won&#39;t be available for the users")


def test_book_detail_page_does_not_show_warning_message_to_user_if_no_specimens(app, book):
    resp = app.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain(no="Please add a specimen, or the book won&#39;t be available for the users")


def test_book_detail_page_does_not_show_warning_message_if_specimens(staffapp, book):
    BookSpecimenFactory(item=book)
    resp = staffapp.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain(no="Please add a specimen, or the book won&#39;t be available for the users")


def test_book_detail_page_does_not_show_warning_message_if_digital_specimens(staffapp, book):
    DigitalBookSpecimenFactory(item=book)
    resp = staffapp.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain(no="Please add a specimen, or the book won&#39;t be available for the users")


def test_book_detail_page_list_physical_specimens_to_staff(staffapp, book):
    specimen = BookSpecimenFactory(item=book, barcode='123789')
    resp = staffapp.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain(specimen.barcode)


def test_book_detail_page_list_digital_specimens_to_staff(staffapp, book):
    DigitalBookSpecimenFactory(item=book)
    resp = staffapp.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain('Digital specimen')


def test_book_detail_allow_to_download_digital_specimen(app, book):
    DigitalBookSpecimenFactory(item=book, file__filename='book.epub')
    resp = app.get(reverse('library:book_detail', kwargs={'pk': book.pk}))
    resp.mustcontain('Download epub')


def test_anonymous_should_not_access_book_create_page(app):
    assert app.get(reverse('library:book_create'), status=302)


def test_non_staff_should_not_access_book_create_page(loggedapp):
    assert loggedapp.get(reverse('library:book_create'), status=302)


def test_staff_should_access_book_create_page(staffapp):
    assert staffapp.get(reverse('library:book_create'), status=200)


def test_anonymous_should_not_access_book_update_page(app, book):
    assert app.get(reverse('library:book_update',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_book_update_page(loggedapp, book):
    assert loggedapp.get(reverse('library:book_update',
                         kwargs={'pk': book.pk}), status=302)


def test_anonymous_should_not_access_book_delete_page(app, book):
    assert app.get(reverse('library:book_delete',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_book_delete_page(loggedapp, book):
    assert loggedapp.get(reverse('library:book_delete',
                         kwargs={'pk': book.pk}), status=302)


def test_anonymous_should_not_access_specimen_delete_page(app, book):
    assert app.get(reverse('library:specimen_delete',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_specimen_delete_page(loggedapp, book):
    assert loggedapp.get(reverse('library:specimen_delete',
                         kwargs={'pk': book.pk}), status=302)


def test_staff_should_access_book_update_page(staffapp, book):
    assert staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book.pk}), status=200)


def test_staff_can_create_book(staffapp):
    form = staffapp.get(reverse('library:book_create')).forms['model_form']
    assert not Book.objects.count()
    form['name'] = 'My book title'
    form['description'] = 'My book summary'
    form['section'] = 'digital'
    form.submit().follow()
    assert Book.objects.count() == 1


def test_staff_can_edit_book(staffapp, book):
    form = staffapp.get(reverse('library:book_update',
                                kwargs={'pk': book.pk})).forms['model_form']
    title = "New title"
    assert Book.objects.get(pk=book.pk).name != title
    form['name'] = title
    form.submit().follow()
    assert Book.objects.get(pk=book.pk).name == title


def test_staff_user_can_delete_book(staffapp, book):
    assert Book.objects.count() == 1
    url = reverse('library:book_delete', kwargs={'pk': book.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert not Book.objects.count()


def test_staff_can_create_specimen(staffapp, book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form['barcode'] = '23135321'
    response = form.submit()
    print(response)
    response.follow()
    assert book.specimens.count()


def test_staff_can_edit_specimen(staffapp, specimen):
    url = reverse('library:specimen_update', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).forms['model_form']
    comments = "This is a new comment"
    assert BookSpecimen.objects.get(pk=specimen.pk).comments != comments
    form['comments'] = comments
    form.submit().follow()
    assert BookSpecimen.objects.get(pk=specimen.pk).comments == comments


def test_staff_user_can_delete_specimen(staffapp, specimen):
    assert BookSpecimen.objects.count() == 1
    assert Book.objects.count() == 1
    url = reverse('library:specimen_delete', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert Book.objects.count() == 1
    assert not BookSpecimen.objects.count()


def test_it_should_be_possible_to_create_several_books_without_isbn(staffapp):
    assert not Book.objects.count()
    url = reverse('library:book_create')
    form = staffapp.get(url).forms['model_form']
    form['name'] = 'My book title'
    form['description'] = 'My book summary'
    form['section'] = 'digital'
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(url).forms['model_form']
    form['name'] = 'My book title 2'
    form['description'] = 'My book summary 2'
    form['section'] = 'children-cartoons'
    form['isbn'] = ''
    form.submit().follow()
    assert Book.objects.count() == 2


def test_it_should_be_possible_to_remove_isbn_from_books(staffapp):
    book1 = BookFactory(isbn='123456')
    book2 = BookFactory(isbn='321564987')
    assert not Book.objects.filter(isbn__isnull=True)
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book1.pk})).forms['model_form']
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book2.pk})).forms['model_form']
    form['isbn'] = ''
    form.submit().follow()
    assert len(Book.objects.filter(isbn__isnull=True)) == 2


def test_should_keep_only_numbers_in_isbn(staffapp):
    form = staffapp.get(reverse('library:book_create')).forms['model_form']
    assert not Book.objects.count()
    form['name'] = 'My book title'
    form['description'] = 'My book summary'
    form['section'] = 'digital'
    form['isbn'] = '2-7071-2402-8'
    form.submit().follow()
    assert Book.objects.get(isbn='2707124028')


def test_import_from_isbn(staffapp, monkeypatch):
    doc = b"""{"ISBN:2070379043": {"publishers": [{"name": "Gallimard"}], "identifiers": {"isbn_13": ["9782070379040"], "openlibrary": ["OL8838456M"], "isbn_10": ["2070379043"], "goodreads": ["118988"], "librarything": ["1655982"]}, "weight": "7 ounces", "title": "Les Enchanteurs", "url": "https://openlibrary.org/books/OL8838456M/Les_enchanteurs", "number_of_pages": 373, "cover": {"small": "https://covers.openlibrary.org/b/id/967767-S.jpg", "large": "https://covers.openlibrary.org/b/id/967767-L.jpg", "medium": "https://covers.openlibrary.org/b/id/967767-M.jpg"}, "publish_date": "January 22, 1988", "key": "/books/OL8838456M", "authors": [{"url": "https://openlibrary.org/authors/OL123692A/Romain_Gary", "name": "Romain Gary"}]}}"""  # noqa
    monkeypatch.setattr('ideascube.library.utils.load_cover_from_url',
                        lambda x: 'xxx')
    monkeypatch.setattr('ideascube.library.utils.read_url', lambda x: doc)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_isbn'] = '2070379043'
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 1
    book = Book.objects.last()
    # Only one notice processed, we should have been redirected to its page.
    assert response.location.endswith(book.get_absolute_url())


def test_import_from_files(staffapp, monkeypatch):
    assert Book.objects.count() == 0
    monkeypatch.setattr('ideascube.library.utils.read_url', lambda x: None)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload('ideascube/library/tests/data/moccam.csv')
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2

    book = Book.objects.last()
    assert book.name == 'Les Enchanteurs'
    assert book.description.startswith(
        "Le narrateur, Fosco Zaga, est un vieillard. Hors d'âge. Deux cents ")
    assert book.isbn == '9782070379040'
    assert book.authors == 'Romain Gary'
    assert book.publisher == 'Gallimard'

    book = Book.objects.first()
    assert book.name == 'Le petit prince'
    assert book.description.startswith(
        "«Le premier soir je me suis donc endormi sur le sable à mille ")
    assert book.isbn == '9782070612758'
    assert book.authors == 'Antoine de Saint-Exupéry'
    assert book.publisher == 'Gallimard'


def test_import_from_files_does_not_duplicate(staffapp, monkeypatch):
    monkeypatch.setattr('ideascube.library.utils.read_url', lambda x: None)
    path = 'ideascube/library/tests/data/moccam.csv'
    with open(path, encoding='utf-8') as f:
        isbn = f.read().split('\t')[0]
    # Create a book with same isbn as first entry of CSV.
    BookFactory(isbn=isbn)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload(path)
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2


def test_import_from_files_load_cover_if_exists(staffapp, monkeypatch):
    assert Book.objects.count() == 0
    image = 'ideascube/tests/data/the-prophet.jpg'
    monkeypatch.setattr(
        'ideascube.library.utils.read_url',
        lambda x: open(image, 'rb').read()
    )
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload('ideascube/library/tests/data/moccam.csv')
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2
    assert Book.objects.last().cover
    assert open(Book.objects.last().cover.path, 'rb').read() == open(image, 'rb').read()


def test_import_from_ideascube_export(staffapp, monkeypatch):
    expected = {
        'isbn': '123456',
        'authors': 'Marcel Pagnol',
        'serie': "L'Eau des collines",
        'name': 'Jean de Florette',
        'description': u"Les Bastides Blanches, c'était une paroisse de cent cinquante habitants, perchée sur la proue de l'un des derniers contreforts du massif de l'Étoile, à deux lieues d'Aubagne… Une route de terre y conduisait par une montée si abrupte que de loin elle paraissait verticale : mais du côté des collines il n'en sortait qu'un chemin muletier d'où partaient quelques sentiers qui menaient au ciel.",  # noqa
        'publisher': u'Éditions de Provence',
        'lang': 'fr',
    }
    BookFactory(**expected)
    resp = staffapp.get(reverse('library:book_export'))
    Book.objects.all().delete()
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['files_format'] = 'ideascube'
    form['from_files'] = Upload('archive.zip', resp.content,
                                'application/zip')
    response = form.submit()
    response.follow()
    assert Book.objects.count()
    book = Book.objects.last()
    for name, value in expected.items():
        assert getattr(book, name) == value
    assert book.cover


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = BookSpecimenFactory(item__tags=['plane'])
    boat = BookSpecimenFactory(item__tags=['boat'])
    response = app.get(reverse('library:index'), {'tags': 'plane'})
    assert plane.item.name in response.content.decode()
    assert boat.item.name not in response.content.decode()


def test_by_kind_page_should_be_filtered_by_section_kind(app):
    digital = BookSpecimenFactory(item__section='digital')
    myth = BookSpecimenFactory(item__section='adults-myths')
    response = app.get(reverse('library:index'), {'kind': 'digital'})
    assert digital.item.name in response.content.decode()
    assert myth.item.name not in response.content.decode()


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    BookSpecimenFactory.create_batch(size=4, item__tags=['plane'])
    url = reverse('library:index')
    response = app.get(url, {'tags': 'plane'})
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url, {'tags': 'plane', 'page': 2})
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url, {'tags': 'plane', 'page': 3}, status=404)


def test_can_create_book_with_tags(staffapp):
    url = reverse('library:book_create')
    form = staffapp.get(url).forms['model_form']
    form['name'] = 'My book title'
    form['description'] = 'My book summary'
    form['section'] = 'digital'
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    book = Book.objects.last()
    assert book.tags.count() == 2
    assert book.tags.first().name == 'tag1'


def test_can_update_book_tags(staffapp, book):
    assert book.tags.count() == 0
    url = reverse('library:book_update', kwargs={'pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    other = Book.objects.get(pk=book.pk)
    assert other.tags.count() == 2
    assert other.tags.first().name == 'tag1'


def test_cannot_create_digital_specimen_when_barcode_and_file_not_set(staffapp,
                                                                      book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form.submit()
    assert not book.specimens.count()


def test_cannot_create_digital_specimen_when_barcode_and_file_are_set(staffapp,
                                                                      book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form['barcode'] = '123456'
    form['file'] = Upload('ideascube/library/tests/data/test-digital')
    form.submit()
    assert not book.specimens.count()


def test_when_only_file_is_set_specimen_is_created_as_digital(staffapp, book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form['file'] = Upload('ideascube/library/tests/data/test-digital')
    form.submit()
    assert book.specimens.count()
    assert not BookSpecimen.objects.last().physical


def test_when_only_barcode_is_set_specimen_is_created_as_not_digital(staffapp,
                                                                     book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form['barcode'] = '123456'
    form.submit()
    assert book.specimens.count()
    assert BookSpecimen.objects.last().physical


def test_anonymous_cannot_export_book_notices(app):
    assert app.get(reverse('library:book_export'), status=302)


def test_non_staff_cannot_export_book_notices(loggedapp):
    assert loggedapp.get(reverse('library:book_export'), status=302)


def test_export_book_notices(staffapp, monkeypatch):
    book1 = BookFactory(isbn="123456", name="my book title")
    name_utf8 = u'النبي (كتاب)'
    BookFactory(isbn="654321", name=name_utf8)
    monkeypatch.setattr(BookExport, 'get_filename', lambda s: 'myfilename')
    resp = staffapp.get(reverse('library:book_export'))
    assert 'myfilename.zip' in resp['Content-Disposition']
    content = ContentFile(resp.content)
    assert zipfile.is_zipfile(content)
    archive = zipfile.ZipFile(content)
    cover_name = '{}.jpg'.format(book1.pk)
    assert cover_name in archive.namelist()
    assert 'myfilename.csv' in archive.namelist()
    assert len(archive.namelist()) == 3
    csv_content = archive.open('myfilename.csv').read().decode('utf-8')
    assert csv_content.startswith(
        'isbn,authors,serie,name,subtitle,description,publisher,section,lang,'
        'cover,tags\r\n')
    assert "my book title" in csv_content
    assert cover_name in csv_content
    assert name_utf8 in csv_content


def test_export_book_specimens(staffapp, monkeypatch):
    book1 = BookFactory(isbn="123456", name="my book title")
    specimen1 = BookSpecimenFactory(item=book1)
    book2 = BookFactory(isbn="654321", name='ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ)')
    specimen2 = DigitalBookSpecimenFactory(item=book2)

    monkeypatch.setattr(
        BookSpecimenExport, 'get_filename', lambda s: 'specimens')

    resp = staffapp.get(reverse('library:specimen_export'))
    assert 'specimens.zip' in resp['Content-Disposition']

    with zipfile.ZipFile(ContentFile(resp.content)) as archive:
        epubname = '{}.epub'.format(specimen2.pk)
        assert sorted(archive.namelist()) == [epubname, 'specimens.csv']
        csv = archive.open('specimens.csv').read().decode('utf-8').strip()
        assert csv.split('\r\n') == [
            'isbn,title,barcode,serial,comments,location,file',
            '{},{},{},,,,'.format(
                specimen1.item.isbn, specimen1.item.name, specimen1.barcode),
            '{},{},,,,,{}'.format(
                specimen2.item.isbn, specimen2.item.name, epubname),
        ]


def test_import_book_specimens(staffapp, tmpdir):
    book1 = BookFactory(isbn='123456', name='my book title')
    book2 = BookFactory(isbn='234567', name='ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ)')
    BookFactory(isbn='345678', name='my book title')

    zip_path = tmpdir.join('specimens.zip')
    csv_content = '\n'.join([
        'isbn,title,barcode,serial,comments,location,file',
        '123456,my book title,1234,,,,',
        '123456,my book title,,,,,1.epub',
        '234567,ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ),,,,,2.epub',
        '234567,ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ),1234,,,,',
        '123456,no such book,2345,,,,',
        ',ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ),3456,,,,',
        ',no such book,1234,,,,',
        ',my book title,1234,,,,',
        '987654,ﺎﻠﻨﺒﻳ (ﻚﺗﺎﺑ),1234,,,,',
    ])

    with zipfile.ZipFile(str(zip_path), mode='w') as zip:
        zip.writestr('specimens.csv', csv_content.encode('utf-8'))
        zip.writestr('2.epub', b'Trust me, this is an epub')

    form = staffapp.get(reverse('library:specimen_import')).forms['import']
    form['source'] = Upload(
        zip_path.basename, zip_path.read_binary(), 'application/zip')
    response = form.submit()
    assert response.status_int == 302
    assert response.location.endswith(reverse('library:index'))

    response = response.follow()
    specimens = BookSpecimen.objects.order_by('id')
    assert specimens.count() == 4

    # CSV line 2
    specimen = specimens[0]
    assert specimen.item.pk == book1.pk
    assert specimen.barcode == '1234'
    assert specimen.serial is None
    assert specimen.comments == ''
    assert specimen.location == ''
    assert not specimen.file

    # CSV line 3
    assert (
        'Could not import line 3: file 1.epub is missing from the archive'
    ) in response

    # CSV line 4
    specimen = specimens[1]
    assert specimen.item.pk == book2.pk
    assert specimen.barcode is None
    assert specimen.serial is None
    assert specimen.comments == ''
    assert specimen.location == ''
    assert specimen.file.read() == b'Trust me, this is an epub'

    # CSV line 5
    assert (
        'Could not import line 5: barcode: * Specimen with this Ideascube bar '
        'code already exists.'
    ) in response

    # CSV line 6
    specimen = specimens[2]
    assert specimen.item.pk == book1.pk
    assert specimen.barcode == '2345'
    assert specimen.serial is None
    assert specimen.comments == ''
    assert specimen.location == ''
    assert not specimen.file

    # CSV line 7
    specimen = specimens[3]
    assert specimen.item.pk == book2.pk
    assert specimen.barcode == '3456'
    assert specimen.serial is None
    assert specimen.comments == ''
    assert specimen.location == ''
    assert not specimen.file

    # CSV line 8
    assert (
        'Could not import line 8: no &quot;no such book&quot; book'
    ) in response

    # CSV line 9
    assert (
        'Could not import line 9: found multiple &quot;my book title&quot; '
        'books') in response

    # CSV line 10
    assert (
        'Could not import line 10: no book with ISBN &quot;987654&quot;'
        ) in response


def test_import_book_specimens_without_zip(staffapp, tmpdir):
    path = tmpdir.join('specimens.txt')
    path.write('This is a text file')

    form = staffapp.get(reverse('library:specimen_import')).forms['import']
    form['source'] = Upload(path.basename, path.read_binary(), 'text/plain')
    response = form.submit()
    assert response.status_int == 200
    assert 'Uploaded file is not a Zip archive' in response
    assert BookSpecimen.objects.count() == 0


def test_import_book_specimens_without_csv(staffapp, tmpdir):
    zip_path = tmpdir.join('specimens.zip')

    with zipfile.ZipFile(str(zip_path), mode='w') as zip:
        zip.writestr('2.epub', b'Trust me, this is an epub')

    form = staffapp.get(reverse('library:specimen_import')).forms['import']
    form['source'] = Upload(
        zip_path.basename, zip_path.read_binary(), 'application/zip')
    response = form.submit()
    assert response.status_int == 200
    assert 'Archive does not contain a CSV' in response
    assert BookSpecimen.objects.count() == 0
