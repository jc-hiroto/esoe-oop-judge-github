# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2020-03-13 15:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0020_problem_staff_viewable_only'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='bitbucket_account',
            new_name='github_account',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='bitbucket_repository',
            new_name='github_repository',
        ),
    ]
