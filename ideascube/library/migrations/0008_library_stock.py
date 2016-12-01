# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers

import ideascube.models


def migrate_data(apps, schema_editor):
    OldBook = apps.get_model('library', 'OldBook')
    Book = apps.get_model('library', 'Book')
    BookSpecimen = apps.get_model('library', 'BookSpecimen')

    db_alias = schema_editor.connection.alias

    for old_book in OldBook.objects.using(db_alias).order_by('created_at'):
        new_book = Book(
            module='library', name=old_book.title,
            description=old_book.summary,
            # And now the stuff which hasn't changed
            isbn=old_book.isbn, authors=old_book.authors, serie=old_book.serie,
            subtitle=old_book.subtitle, publisher=old_book.publisher,
            section=old_book.section, lang=old_book.lang, cover=old_book.cover,
            tags=old_book.tags)
        new_book.save()

        for old_bookspecimen in old_book.specimens.all():
            new_bookspecimen = BookSpecimen(
                barcode=old_bookspecimen.serial, item=new_book, count=1,
                comments=old_bookspecimen.remarks,
                # And now the stuff which hasn't changed
                location=old_bookspecimen.location, file=old_bookspecimen.file)
            new_bookspecimen.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('monitoring', '0004_auto_20161007_1240'),
        ('taggit', '0002_auto_20150616_2121'),
        ('library', '0007_auto_20161007_1220'),
    ]

    operations = [
        migrations.RenameModel('BookSpecimen', 'OldBookSpecimen'),
        migrations.RenameModel('Book', 'OldBook'),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('stockitem_ptr', models.OneToOneField(
                    auto_created=True, on_delete=models.deletion.CASCADE,
                    parent_link=True, primary_key=True, serialize=False,
                    to='monitoring.StockItem')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='creation date')),
                ('modified_at', models.DateTimeField(
                    auto_now=True, verbose_name='modification date')),
                ('isbn', models.CharField(
                    blank=True, max_length=40, null=True, unique=True)),
                ('authors', models.CharField(
                    blank=True, max_length=300, verbose_name='authors')),
                ('serie', models.CharField(
                    blank=True, max_length=300, verbose_name='serie')),
                ('subtitle', models.CharField(
                    blank=True, max_length=300, verbose_name='subtitle')),
                ('publisher', models.CharField(
                    blank=True, max_length=100, verbose_name='publisher')),
                ('section', models.PositiveSmallIntegerField(
                    choices=[
                        (1, 'digital'), (2, 'children - cartoons'),
                        (3, 'children - novels'), (10, 'children - poetry'),
                        (11, 'children - theatre'),
                        (4, 'children - documentary'),
                        (5, 'children - comics'), (6, 'adults - novels'),
                        (12, 'adults - poetry'), (13, 'adults - theatre'),
                        (7, 'adults - documentary'), (8, 'adults - comics'),
                        (9, 'game'), (99, 'other')], verbose_name='section')),
                ('lang', ideascube.models.LanguageField(
                    choices=[
                        ('af', 'Afrikaans'), ('am', 'አማርኛ'),
                        ('ar', 'العربيّة'), ('ast', 'Asturianu'),
                        ('az', 'Azərbaycanca'), ('be', 'Беларуская'),
                        ('bg', 'Български'), ('bm', 'Bambara'),
                        ('bn', 'বাংলা'), ('br', 'Brezhoneg'),
                        ('bs', 'Bosanski'), ('ca', 'Català'),
                        ('ckb', 'سۆرانی'), ('cs', 'Česky'), ('cy', 'Cymraeg'),
                        ('da', 'Dansk'), ('de', 'Deutsch'),
                        ('dsb', 'Dolnoserbski'), ('el', 'Ελληνικά'),
                        ('en', 'English'), ('en-au', 'Australian english'),
                        ('en-gb', 'British english'), ('eo', 'Esperanto'),
                        ('es', 'Español'), ('es-ar', 'Español de argentina'),
                        ('es-co', 'Español de colombia'),
                        ('es-mx', 'Español de mexico'),
                        ('es-ni', 'Español de nicaragua'),
                        ('es-ve', 'Español de venezuela'), ('et', 'Eesti'),
                        ('eu', 'Basque'), ('fa', 'فارسی'), ('fi', 'Suomi'),
                        ('fr', 'Français'), ('fy', 'Frysk'), ('ga', 'Gaeilge'),
                        ('gd', 'Gàidhlig'), ('gl', 'Galego'), ('he', 'עברית'),
                        ('hi', 'Hindi'), ('hr', 'Hrvatski'),
                        ('hsb', 'Hornjoserbsce'), ('hu', 'Magyar'),
                        ('ia', 'Interlingua'), ('id', 'Bahasa indonesia'),
                        ('io', 'Ido'), ('is', 'Íslenska'), ('it', 'Italiano'),
                        ('ja', '日本語'), ('ka', 'ქართული'), ('kk', 'Қазақ'),
                        ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', '한국어'),
                        ('ku', 'Kurdî'), ('lb', 'Lëtzebuergesch'),
                        ('ln', 'Lingála'), ('lt', 'Lietuviškai'),
                        ('lv', 'Latviešu'), ('mk', 'Македонски'),
                        ('ml', 'Malayalam'), ('mn', 'Mongolian'),
                        ('mr', 'मराठी'), ('my', 'မြန်မာဘာသာ'),
                        ('nb', 'Norsk (bokmål)'), ('ne', 'नेपाली'),
                        ('nl', 'Nederlands'), ('nn', 'Norsk (nynorsk)'),
                        ('no', 'Norsk'), ('os', 'Ирон'), ('pa', 'Punjabi'),
                        ('pl', 'Polski'), ('ps', 'پښتو'), ('pt', 'Português'),
                        ('pt-br', 'Português brasileiro'), ('rn', 'Kirundi'),
                        ('ro', 'Română'), ('ru', 'Русский'),
                        ('sk', 'Slovensky'), ('sl', 'Slovenščina'),
                        ('so', 'Af-soomaali'), ('sq', 'Shqip'),
                        ('sr', 'Српски'), ('sr-latn', 'Srpski (latinica)'),
                        ('sv', 'Svenska'), ('sw', 'Kiswahili'),
                        ('ta', 'தமிழ்'), ('te', 'తెలుగు'), ('th', 'ภาษาไทย'),
                        ('ti', 'ትግርኛ'), ('tr', 'Türkçe'), ('tt', 'Татарча'),
                        ('udm', 'Удмурт'), ('uk', 'Українська'),
                        ('ur', 'اردو'), ('vi', 'Tiếng việt'),
                        ('wo', 'Wolof'), ('zh-hans', '简体中文'),
                        ('zh-hant', '繁體中文')
                    ], max_length=10, verbose_name='Language')),
                ('cover', models.ImageField(
                    blank=True, upload_to='library/cover',
                    verbose_name='cover')),
                ('tags', taggit.managers.TaggableManager(
                    blank=True, help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem', to='taggit.Tag',
                    verbose_name='Tags')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=('monitoring.stockitem', models.Model),
        ),
        migrations.CreateModel(
            name='BookSpecimen',
            fields=[
                ('specimen_ptr', models.OneToOneField(
                    auto_created=True, on_delete=models.deletion.CASCADE,
                    parent_link=True, primary_key=True, serialize=False,
                    to='monitoring.Specimen')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='creation date')),
                ('modified_at', models.DateTimeField(
                    auto_now=True, verbose_name='modification date')),
                ('location', models.CharField(
                    blank=True, max_length=300, verbose_name='location')),
                ('file', models.FileField(
                    blank=True, upload_to='library/digital',
                    verbose_name='digital file')),
            ],
            options={
                'ordering': ['-modified_at'],
                'abstract': False,
            },
            bases=('monitoring.specimen', models.Model),
        ),
        migrations.RunPython(
            migrate_data, migrations.RunPython.noop,
            hints={'using': 'default'}),
        migrations.DeleteModel('OldBookSpecimen'),
        migrations.DeleteModel('OldBook'),
    ]
