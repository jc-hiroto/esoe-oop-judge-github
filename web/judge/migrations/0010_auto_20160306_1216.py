# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-06 12:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0009_auto_20160306_0945'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='detail_message',
            new_name='detail_messages',
        ),
    ]
