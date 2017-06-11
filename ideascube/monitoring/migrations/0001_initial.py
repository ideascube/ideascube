# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('module', models.CharField(max_length=20, choices=[(b'cinema', 'Cinema'), (b'library', 'Library'), (b'digital', 'Multimedia')])),
                ('activity', models.CharField(max_length=200, blank=True)),
                ('partner', models.CharField(max_length=200, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'entry',
                'verbose_name_plural': 'entries',
            },
        ),
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
        ),
        migrations.CreateModel(
            name='InventorySpecimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=1)),
                ('inventory', models.ForeignKey(to='monitoring.Inventory', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(default=datetime.date.today, verbose_name='Due date')),
                ('returned_at', models.DateTimeField(default=None, null=True, verbose_name='Return time', blank=True)),
                ('comments', models.CharField(max_length=500, verbose_name='Comments', blank=True)),
                ('by', models.ForeignKey(related_name='loans_made', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('due_date', 'created_at'),
            },
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('barcode', models.CharField(max_length=40, unique=True, null=True, verbose_name='ideascube bar code', blank=True)),
                ('serial', models.CharField(max_length=100, null=True, verbose_name='Serial number', blank=True)),
                ('count', models.IntegerField(default=1)),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(max_length=20, choices=[(b'cinema', 'Cinema'), (b'library', 'Library'), (b'digital', 'Multimedia'), (b'admin', 'Administration'), (b'other', 'Other')])),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
            ],
            options={
                'ordering': ('module', 'name'),
            },
        ),
        migrations.AddField(
            model_name='specimen',
            name='item',
            field=models.ForeignKey(related_name='specimens', to='monitoring.StockItem', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='loan',
            name='specimen',
            field=models.ForeignKey(to='monitoring.Specimen', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='loan',
            name='user',
            field=models.ForeignKey(related_name='loans', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='inventoryspecimen',
            name='specimen',
            field=models.ForeignKey(to='monitoring.Specimen', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='inventoryspecimen',
            unique_together=set([('inventory', 'specimen')]),
        ),
    ]
