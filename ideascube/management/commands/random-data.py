# -*- coding: utf-8 -*-

from datetime import date, datetime, timezone
import os
import random

from django.conf import locale, settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django_countries.data import COUNTRIES

from ideascube.blog.models import Content
from ideascube.configuration import set_config
from ideascube.library.models import Book, BookSpecimen
from ideascube.mediacenter.models import Document
from ideascube.monitoring.models import (
    Entry,
    Inventory,
    InventorySpecimen,
    Loan,
    Specimen,
    StockItem,
)


def get_random_boolean(optional=True):
    if optional and random.choice([True, False]):
        return None

    return random.choice([True, False])


def get_random_date(start, end, optional=True):
    if optional and random.choice([True, False]):
        return None

    return date(
        random.randint(start, end),
        random.randint(1, 12),
        random.randint(1, 28))


def get_random_datetime(start, end, optional=True):
    if optional and random.choice([True, False]):
        return None

    return datetime(
        random.randint(start, end),
        random.randint(1, 12),
        random.randint(1, 28),
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
        tzinfo=timezone.utc)


def get_random_int(start, end, optional=True):
    if optional and random.choice([True, False]):
        return None

    return random.randint(start, end)


def get_random_string(length=10, optional=True):
    if optional and random.choice([True, False]):
        return ''

    CHARS = 'abcdefghijklmnopqrstuvwxyzàâéèêîôû木林森.'
    result = []

    for i in range(length):
        if optional and random.choice([True, False]):
            result.append('')

        else:
            result.append(random.choice(CHARS))

    return ''.join(result)


def get_random_multi_strings(min=0, max=1, joiner=',', optional=True):
    if optional and random.choice([True, False]):
        return ''

    result = []

    for i in range(get_random_int(min, max, optional=False)):
        result.append(get_random_string(optional=False))

    return joiner.join(result)


def get_random_choice(choices, optional=True):
    choices = [c[0] if isinstance(c, tuple) else c for c in choices]

    if optional:
        choices.append('')

    return random.choice(choices)


def get_random_choice_list(choices, optional=True):
    result = []

    if optional and random.choice([True, False]):
        return result

    choices = [c[0] if isinstance(c, tuple) else c for c in choices]

    for item in choices:
        if random.choice([True, False]):
            result.append(item)

    return result


class Command(BaseCommand):
    help = 'Populate the database with lots of random data'

    def _progress(self):
        self.stdout.write('.', ending='')
        self.stdout.flush()

    def handle(self, *args, **options):
        if not settings.DEBUG:
            msg = ('This does not seem to be a dev project. Aborting. You need'
                   ' to be in DEBUG=True')
            raise CommandError(msg)

        ALL_TAGS = ['tag%d' % i for i in range(1, 31)]
        # Let's not worry with all of them, just use the ones for which we can
        # easily have real files.
        MEDIA_KIND_CHOICES = [
            Document.IMAGE, Document.OTHER, Document.PDF, Document.TEXT,
            Document.VIDEO]
        MEDIA_FILE_PATHS = {
            Document.IMAGE: 'ideascube/mediacenter/tests/data/an-image.jpg',
            Document.PDF: 'ideascube/mediacenter/tests/data/a-pdf.pdf',
            Document.VIDEO: 'ideascube/mediacenter/tests/data/a-video.mp4',
        }
        User = get_user_model()

        self.stdout.write('Creating users')

        for i in range(50):
            user = User(
                ar_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                birth_year=get_random_int(1917, 2017),
                box_awareness=get_random_choice(User.BOX_AWARENESS_CHOICES),
                camp_activities=get_random_choice_list(User.CAMP_ACTIVITY_CHOICES),
                camp_address=get_random_string(),
                camp_entry_date=get_random_date(2000, 2017),
                children_above_18=get_random_int(0, 3),
                children_under_12=get_random_int(0, 3),
                children_under_18=get_random_int(0, 3),
                city=get_random_string(),
                country=get_random_choice(COUNTRIES),
                country_of_origin_occupation=get_random_string(),
                current_occupation=get_random_choice(User.OCCUPATION_CHOICES),
                disabilities=get_random_choice_list(User.DISABILITY_CHOICES),
                email='test.user%d@ideascube.org' % i,
                en_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                extra=get_random_string(),
                fa_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                family_status=get_random_choice(User.FAMILY_STATUS_CHOICES),
                fr_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                full_name=get_random_string(),
                gender=get_random_choice(User.GENDER_CHOICES),
                id_card_number=get_random_string(),
                is_sent_to_school=get_random_boolean(optional=False),
                is_staff=(i < 10),
                ku_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                latin_name=get_random_string(),
                marital_status=get_random_choice(User.MARITAL_STATUS_CHOICES),
                phone=get_random_multi_strings(max=3),
                refugee_id=get_random_string(),
                rn_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                school_level=get_random_choice(User.SCHOOL_LEVEL_CHOICES),
                sdb_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
                serial='user%d' % i,
                short_name=get_random_string(),
                sw_level=get_random_choice_list(User.LANG_KNOWLEDGE_CHOICES),
            )
            user.save()

            if get_random_boolean(optional=False):
                user.set_password(get_random_string())

            self._progress()

        # Those will be useful later
        users = list(User.objects.all())
        staff = list(User.objects.filter(is_staff=True))

        self.stdout.write('\nCreating configurations')

        actor = get_random_choice(staff, optional=False)
        value = get_random_choice_list(locale.LANG_INFO)

        if value:
            set_config('content', 'local-languages', value, actor)

        self._progress()

        actor = get_random_choice(staff, optional=False)
        value = get_random_choice_list([
            'artes.es', 'gastronomia-colombiana.es',
            'danzas-populares-y-nacionales.es', 'dirtybiology.fr',
            'wikibooks.fa', 'wikipedia.fr'])

        if value:
            set_config('home-page', 'displayed-package-ids', value, actor)

        self._progress()

        actor = get_random_choice(staff, optional=False)
        value = get_random_string()

        if value:
            set_config('server', 'site-name', value, actor)

        self._progress()

        self.stdout.write('\nCreating media documents')

        for i in range(50):
            kind = get_random_choice(MEDIA_KIND_CHOICES, optional=False)
            original_path = MEDIA_FILE_PATHS.get(kind, __file__)
            preview_path = MEDIA_FILE_PATHS[Document.IMAGE]

            with open(original_path, 'rb') as o, open(preview_path, 'rb') as p:
                original = File(o, name=os.path.basename(o.name))

                if get_random_boolean():
                    preview = File(p, name=os.path.basename(p.name))

                else:
                    preview = None

                doc = Document(
                    title=get_random_string(optional=False),
                    summary=get_random_string(optional=False),
                    lang=get_random_choice(locale.LANG_INFO),
                    original=original,
                    preview=preview,
                    credits=get_random_string(optional=False),
                    kind=kind,
                    package_id=get_random_string(),
                )
                doc.save()

                if get_random_boolean(optional=False):
                    doc.tags.add(*get_random_choice_list(ALL_TAGS))

            self._progress()

        self.stdout.write('\nCreating blog articles')

        for i in range(50):
            author = get_random_choice(staff, optional=False)
            author_text=get_random_choice(
                [author.full_name, get_random_string()])
            image_path = MEDIA_FILE_PATHS[Document.IMAGE]

            with open(image_path, 'rb') as i:
                if get_random_boolean():
                    image = File(i, name=os.path.basename(i.name))

                else:
                    image = None

                article = Content(
                    title=get_random_string(optional=False),
                    author=author,
                    author_text=author_text,
                    summary=get_random_multi_strings(max=10, joiner=' '),
                    image=image,
                    text=get_random_multi_strings(max=100, joiner=' '),
                    published_at=get_random_datetime(
                        2015, 2020, optional=False),
                    status=get_random_choice(Content.STATUSES, optional=False),
                    lang=get_random_choice(locale.LANG_INFO),
                )
                article.save()

                if get_random_boolean(optional=False):
                    article.tags.add(*get_random_choice_list(ALL_TAGS))

            self._progress()

        self.stdout.write('\nCreating library books and specimens')

        for i in range(50):
            cover_path = MEDIA_FILE_PATHS[Document.IMAGE]
            isbn = get_random_string() or None

            with open(cover_path, 'rb') as c:
                if get_random_boolean():
                    cover = File(c, name=os.path.basename(c.name))

                else:
                    cover = None

                book = Book(
                    name=get_random_string(optional=False),
                    description=get_random_multi_strings(max=20, joiner=' '),
                    isbn=isbn,
                    authors=get_random_multi_strings(max=3, joiner=', '),
                    serie=get_random_string(),
                    subtitle=get_random_string(),
                    publisher=get_random_string(),
                    section=get_random_choice(
                        Book.SECTION_CHOICES, optional=False),
                    lang=get_random_choice(locale.LANG_INFO),
                    cover=cover,
                )
                book.save()

                if get_random_boolean(optional=False):
                    book.tags.add(*get_random_choice_list(ALL_TAGS))

            self._progress()

        self.stdout.write('\n')

        # Those will be useful later
        books = list(Book.objects.all())

        for i in range(100):
            barcode = get_random_string() or None
            serial = get_random_string() or None
            file_path = MEDIA_FILE_PATHS[Document.PDF]

            with open(file_path, 'rb') as f:
                if get_random_boolean(optional=False):
                    file = File(f, name=os.path.basename(f.name))
                    count = 1

                else:
                    file = None
                    count = get_random_int(1, 3, optional=False)

                specimen = BookSpecimen(
                    barcode=barcode,
                    serial=serial,
                    item=get_random_choice(books, optional=False),
                    count=count,
                    comments=get_random_multi_strings(max=20, joiner=' '),
                    location=get_random_string(),
                    file=file,
                )
                specimen.save()

            self._progress()

        self.stdout.write('\nCreating stock items and specimens')

        for i in range(50):
            item = StockItem(
                module=get_random_choice(StockItem.MODULES),
                name=get_random_string(optional=False),
                description=get_random_multi_strings(max=20, joiner=' '),
            )
            item.save()

            self._progress()

        self.stdout.write('\n')

        # Those will be useful later
        items = list(StockItem.objects.all())

        for i in range(100):
            barcode = get_random_string() or None
            serial = get_random_string() or None

            specimen = Specimen(
                barcode=barcode,
                serial=serial,
                item=get_random_choice(items, optional=False),
                count=get_random_int(1, 3, optional=False),
                comments=get_random_multi_strings(max=20, joiner=' '),
            )
            specimen.save()

            self._progress()

        # Those will be useful later
        specimens = list(Specimen.objects.all())

        self.stdout.write('\nCreating inventories')

        for i in range(50):
            inventory = Inventory(
                made_at=get_random_date(2000, 2020, optional=False),
                comments=get_random_multi_strings(max=20, joiner=' '),
            )
            inventory.save()

            self._progress()

        self.stdout.write('\n')

        # Those will be useful later
        inventories = list(Inventory.objects.all())
        seen = set()

        for i in range(100):
            while True:
                inventory = get_random_choice(inventories, optional=False)
                specimen = get_random_choice(specimens, optional=False)

                if (inventory, specimen) not in seen:
                    seen.add((inventory, specimen))
                    break

            inventory_specimen = InventorySpecimen(
                inventory=inventory,
                specimen=specimen,
                count=get_random_int(0, specimen.count, optional=False),
            )
            inventory_specimen.save()

            self._progress()

        self.stdout.write('\nCreating entries')

        for i in range(150):
            entry = Entry(
                module=get_random_choice(Entry.MODULES, optional=False),
                activity=get_random_string(),
                partner=get_random_string(),
                user=get_random_choice(users, optional=False),
            )
            entry.save()

            self._progress()

        self.stdout.write('\nCreating loans')

        for i in range(150):
            loan = Loan(
                specimen=get_random_choice(specimens, optional=False),
                user=get_random_choice(users, optional=False),
                by=get_random_choice(staff, optional=False),
                due_date=get_random_date(2000, 2020, optional=False),
                returned_at=get_random_datetime(2000, 2020),
                comments=get_random_multi_strings(max=20, joiner=' '),
            )
            loan.save()

            self._progress()

        self.stdout.write('\n\nDone.')
