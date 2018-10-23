# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-23 10:50
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('samplesheets', '0004_genericmaterial_alt_names'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assay',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
        migrations.RenameField(
            model_name='genericmaterial',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
        migrations.RenameField(
            model_name='investigation',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
        migrations.RenameField(
            model_name='process',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
        migrations.RenameField(
            model_name='protocol',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
        migrations.RenameField(
            model_name='study',
            old_name='omics_uuid',
            new_name='sodar_uuid'
        ),
    ]
