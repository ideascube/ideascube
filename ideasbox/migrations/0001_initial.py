# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import ideasbox.fields
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IDBUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('serial', models.CharField(unique=True, max_length=40)),
                ('short_name', models.CharField(max_length=30, verbose_name='usual name', blank=True)),
                ('full_name', models.CharField(max_length=100, verbose_name='full name', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('latin_name', models.CharField(max_length=200, verbose_name='Latin written name', blank=True)),
                ('birth_year', models.PositiveSmallIntegerField(null=True, verbose_name='Birth year', blank=True)),
                ('gender', models.CharField(blank=True, max_length=32, verbose_name='Gender', choices=[(b'undefined', 'Undefined'), (b'male', 'Male'), (b'female', 'Female')])),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, verbose_name='Country of origin')),
                ('city', models.CharField(max_length=100, verbose_name='City of origin', blank=True)),
                ('id_card_number', models.CharField(max_length=50, verbose_name='ID card number', blank=True)),
                ('children_under_12', models.PositiveSmallIntegerField(null=True, verbose_name='Number of children under 12', blank=True)),
                ('children_under_18', models.PositiveSmallIntegerField(null=True, verbose_name='Number of children under 18', blank=True)),
                ('children_above_18', models.PositiveSmallIntegerField(null=True, verbose_name='Number of children above 18', blank=True)),
                ('school_level', models.CharField(blank=True, max_length=32, verbose_name='School level', choices=[(b'primary', 'Primary'), (b'secondary', 'Secondary'), (b'professional', 'Professional'), (b'college', 'Higher education')])),
                ('marital_status', models.CharField(blank=True, max_length=32, verbose_name='Marital situation', choices=[(b'couple', 'Couple'), (b'single', 'Single'), (b'widowed', 'Widowed')])),
                ('box_awareness', models.CharField(blank=True, max_length=32, verbose_name='Ideas Box awareness', choices=[(b'seen_box', 'Seen the Box'), (b'partner', 'Has been informed by partner organization'), (b'other_org', 'Has been informed by other organization'), (b'word_of_mouth', 'Word of mouth'), (b'campaign', 'Poster campaign'), (b'other', 'Other')])),
                ('refugee_id', models.CharField(max_length=100, verbose_name='Refugee ID', blank=True)),
                ('camp_entry_date', models.DateField(null=True, verbose_name='Camp entry date', blank=True)),
                ('current_occupation', models.CharField(blank=True, max_length=32, verbose_name='Current occupation', choices=[(b'student', 'Student'), (b'teacher', 'Teacher'), (b'no_profession', 'Without profession'), (b'profit_profession', 'Profit profession'), (b'other', 'Other')])),
                ('country_of_origin_occupation', models.CharField(max_length=100, verbose_name='Occupation in the country of origin', blank=True)),
                ('family_status', models.CharField(blank=True, max_length=32, verbose_name='Family status', choices=[(b'with_family', 'Lives with family in the camp'), (b'no_family', 'Lives without family in the camp'), (b'without_family', 'Has family in the camp but lives without')])),
                ('is_sent_to_school', models.BooleanField(default=False, verbose_name='Sent to school in the country of origin (if under 18)')),
                ('camp_activities', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=512, verbose_name='Activities in the camp', choices=[(b'1', 'Comitees, representation groups'), (b'2', 'Music, dance, singing'), (b'3', 'Other cultural activities'), (b'4', 'Informatic workshops'), (b'5', 'Literacy working group'), (b'6', 'Talking group'), (b'7', 'Recreational'), (b'8', 'Volunteering'), (b'9', 'Psycosocial'), (b'10', 'Educational'), (b'11', 'Sport')])),
                ('camp_address', models.CharField(max_length=200, verbose_name='Address in the camp', blank=True)),
                ('en_level', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=32, verbose_name='English knowledge', choices=[(b'u', 'Understood'), (b'w', 'Written'), (b's', 'Spoken'), (b'r', 'Read')])),
                ('ar_level', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=32, verbose_name='Arabic knowledge', choices=[(b'u', 'Understood'), (b'w', 'Written'), (b's', 'Spoken'), (b'r', 'Read')])),
                ('rn_level', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=32, verbose_name='Kirundi knowledge', choices=[(b'u', 'Understood'), (b'w', 'Written'), (b's', 'Spoken'), (b'r', 'Read')])),
                ('fr_level', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=32, verbose_name='French knowledge', choices=[(b'u', 'Understood'), (b'w', 'Written'), (b's', 'Spoken'), (b'r', 'Read')])),
                ('sw_level', ideasbox.fields.CommaSeparatedCharField(blank=True, max_length=32, verbose_name='Swahili knowledge', choices=[(b'u', 'Understood'), (b'w', 'Written'), (b's', 'Spoken'), (b'r', 'Read')])),
            ],
            options={
                'ordering': ['-modified_at'],
            },
            bases=(models.Model,),
        ),
    ]
