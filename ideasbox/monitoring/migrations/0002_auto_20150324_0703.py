# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('made_at', models.DateField(verbose_name='date')),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
            ],
            options={
                'ordering': ['-modified_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventorySpecimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=1)),
                ('inventory', models.ForeignKey(to='monitoring.Inventory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('barcode', models.CharField(max_length=40, unique=True, null=True, verbose_name='Ideasbox bar code', blank=True)),
                ('serial', models.CharField(max_length=100, null=True, verbose_name='Serial number', blank=True)),
                ('count', models.IntegerField(default=1)),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(max_length=20, choices=[(b'cinema', 'Cinema'), (b'library', 'Library'), (b'digital', 'Digital'), (b'admin', 'Administration'), (b'other', 'Other')])),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
            ],
            options={
                'ordering': ('module', 'name'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='specimen',
            name='item',
            field=models.ForeignKey(related_name='specimens', to='monitoring.StockItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventoryspecimen',
            name='specimen',
            field=models.ForeignKey(to='monitoring.Specimen'),
            preserve_default=True,
        ),
    ]
