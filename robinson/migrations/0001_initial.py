# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sorl.thumbnail.fields
import robinson.models
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExifTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256, verbose_name='Key')),
                ('value', models.TextField(help_text="The human representation of the EXIF tag's value.", null=True, verbose_name='Value', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExifTagSubstitute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256, verbose_name='Key')),
                ('original_value', models.TextField(help_text="EXIF tag's value to replace.", null=True, verbose_name='Original value', blank=True)),
                ('substitute_value', models.TextField(null=True, verbose_name='Substitute value', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'EXIF tag substitute',
                'verbose_name_plural': 'EXIF tag substitutes',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', sorl.thumbnail.fields.ImageField(upload_to=robinson.models.get_photo_upload_path, verbose_name='Photo')),
                ('name', models.CharField(max_length=200, verbose_name='Name', blank=True)),
                ('location', models.CharField(help_text='You are required to specify a location if the JPEG file does not contain geolocation EXIF metadata.<br/>In the event that a JPEG file contains geolocation EXIF metadata, this location will be reverse geocoded and used as the location where the photo was taken.', max_length=200, verbose_name='Location', blank=True)),
                ('location_accuracy', models.SmallIntegerField(default=110, help_text='The estimated accuracy of the location.', verbose_name='Location accuracy', choices=[(0, 'Way off!'), (10, 'Within 100 kilometers'), (20, 'Within 50 kilometers'), (30, 'Within 25 kilometers'), (40, 'Within 15 kilometers'), (50, 'Within 5 kilometers'), (60, 'Within 1 kilometer'), (70, 'Within 500 meters'), (80, 'Within 100 meters'), (90, 'Within 50 meters'), (100, 'Within 25 meters'), (110, 'Within 5 meters')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('filename', models.CharField(verbose_name='Original filename', max_length=256, editable=False)),
                ('estimated_location', models.CharField(verbose_name='Estimated location', max_length=200, null=True, editable=False, blank=True)),
                ('elevation', models.FloatField(verbose_name='Elevation (m)', null=True, editable=False, blank=True)),
                ('latitude', models.FloatField(verbose_name='Latitude', null=True, editable=False, blank=True)),
                ('longitude', models.FloatField(verbose_name='Longitude', null=True, editable=False, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='exiftag',
            name='photo',
            field=models.ForeignKey(to='robinson.Photo'),
        ),
        migrations.AlterUniqueTogether(
            name='exiftag',
            unique_together=set([('key', 'photo')]),
        ),
    ]
