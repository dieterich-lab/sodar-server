# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-10 12:03
from __future__ import unicode_literals

from django.db import migrations

from projectroles.utils import save_default_project_settings


def save_default_settings(apps, schema_editor):
    """Add default settings to existing projects where they haven't been set"""

    Project = apps.get_model('projectroles', 'Project')
    projects = Project.objects.filter(type='PROJECT')   # Exclude categories

    for project in projects:
        save_default_project_settings(project)


class Migration(migrations.Migration):

    dependencies = [
        ('projectroles', '0002_populate_roles'),
    ]

    operations = [
        migrations.RunPython(save_default_settings)
    ]