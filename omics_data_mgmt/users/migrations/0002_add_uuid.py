# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-22 13:16
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='omics_uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='User Omics UUID', unique=False, null=True),
        ),
    ]
