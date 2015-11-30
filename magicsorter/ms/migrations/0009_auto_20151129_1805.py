# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0008_auto_20151129_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scan',
            name='outbox',
        ),
        migrations.AddField(
            model_name='card',
            name='count',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='card',
            name='outbox',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='scan',
            name='image',
            field=models.ImageField(upload_to=b'scans', blank=True),
        ),
    ]
