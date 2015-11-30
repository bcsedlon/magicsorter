# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0007_auto_20151127_2258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scan',
            old_name='withdrawn',
            new_name='outbox',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='result0',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='result1',
        ),
        migrations.AddField(
            model_name='card',
            name='thumb',
            field=models.ImageField(default=datetime.datetime(2015, 11, 29, 13, 58, 50, 986000, tzinfo=utc), upload_to=b'thumbs'),
            preserve_default=False,
        ),
    ]
