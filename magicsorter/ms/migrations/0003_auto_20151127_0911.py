# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0002_auto_20151126_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='hist',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='scan',
            name='result0',
            field=models.FloatField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='scan',
            name='result1',
            field=models.FloatField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='scan',
            name='withdrawn',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
