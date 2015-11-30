# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0009_auto_20151129_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='scan',
            name='outbox',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
