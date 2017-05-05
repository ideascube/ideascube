# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from multiselectfield import MultiSelectField


class CommaSeparatedCharField(MultiSelectField):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0003_auto_20160204_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='ar_level',
            field=CommaSeparatedCharField(blank=True, verbose_name='Arabic knowledge', choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='box_awareness',
            field=models.CharField(blank=True, verbose_name='Ideas Box awareness', choices=[('seen_box', 'Seen the Box'), ('partner', 'Has been informed by partner organization'), ('other_org', 'Has been informed by other organization'), ('word_of_mouth', 'Word of mouth'), ('campaign', 'Poster campaign'), ('other', 'Other')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='camp_activities',
            field=CommaSeparatedCharField(blank=True, verbose_name='Activities in the camp', choices=[('1', 'Comitees, representation groups'), ('2', 'Music, dance, singing'), ('3', 'Other cultural activities'), ('4', 'Informatic workshops'), ('5', 'Literacy working group'), ('6', 'Talking group'), ('7', 'Recreational'), ('8', 'Volunteering'), ('9', 'Psycosocial'), ('10', 'Educational'), ('11', 'Sport')], max_length=512),
        ),
        migrations.AlterField(
            model_name='user',
            name='current_occupation',
            field=models.CharField(blank=True, verbose_name='Current occupation', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('no_profession', 'Without profession'), ('profit_profession', 'Profit profession'), ('other', 'Other')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='en_level',
            field=CommaSeparatedCharField(blank=True, verbose_name='English knowledge', choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='family_status',
            field=models.CharField(blank=True, verbose_name='Family status', choices=[('with_family', 'Lives with family in the camp'), ('no_family', 'Lives without family in the camp'), ('without_family', 'Has family in the camp but lives without')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='fr_level',
            field=CommaSeparatedCharField(blank=True, verbose_name='French knowledge', choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, verbose_name='Gender', choices=[('undefined', 'Undefined'), ('male', 'Male'), ('female', 'Female')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='marital_status',
            field=models.CharField(blank=True, verbose_name='Marital situation', choices=[('couple', 'Couple'), ('single', 'Single'), ('widowed', 'Widowed')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='rn_level',
            field=CommaSeparatedCharField(blank=True, verbose_name='Kirundi knowledge', choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='school_level',
            field=models.CharField(blank=True, verbose_name='School level', choices=[('primary', 'Primary'), ('secondary', 'Secondary'), ('professional', 'Professional'), ('college', 'Higher education')], max_length=32),
        ),
        migrations.AlterField(
            model_name='user',
            name='sw_level',
            field=CommaSeparatedCharField(blank=True, verbose_name='Swahili knowledge', choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], max_length=32),
        ),
    ]
