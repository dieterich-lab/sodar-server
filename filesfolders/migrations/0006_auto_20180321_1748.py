# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-21 16:48
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('filesfolders', '0005_auto_20180105_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='omics_uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='Filesfolders Omics UUID', unique=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='omics_uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='Filesfolders Omics UUID', unique=True),
        ),
        migrations.AlterField(
            model_name='hyperlink',
            name='omics_uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='Filesfolders Omics UUID', unique=True),
        ),
    ]
