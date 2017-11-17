# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-14 16:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectroles', '0003_populate_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectUserTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='STARRED', help_text='Name of tag to be assigned', max_length=64)),
                ('project', models.ForeignKey(help_text='Project in which the tag is assigned', on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='projectroles.Project')),
                ('user', models.ForeignKey(help_text='User for whom the tag is assigned', on_delete=django.db.models.deletion.CASCADE, related_name='project_tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['project__title', 'user__username', 'name'],
            },
        ),
    ]