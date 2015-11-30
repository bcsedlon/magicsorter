# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0005_auto_20151127_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='image',
            field=models.ImageField(upload_to=b'static/cards'),
        ),
        migrations.AlterField(
            model_name='scan',
            name='image',
            field=models.ImageField(upload_to=b'static/scans'),
        ),
    ]
