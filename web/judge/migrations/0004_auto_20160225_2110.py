# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-25 21:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20160223_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='running_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('SU', 'Submitting'), ('SE', 'Submission Error'), ('JU', 'Judging'), ('AC', 'Accepted'), ('PA', 'Partially Accepted'), ('TL', 'Time Limit Exceeded'), ('ML', 'Memory Limit Exceeded'), ('RE', 'Runtime Error'), ('CE', 'Compile Error')], default='SU', max_length=2),
        ),
    ]
