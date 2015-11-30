# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0006_auto_20151127_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='image',
            field=models.ImageField(upload_to=b'cards'),
        ),
        migrations.AlterField(
            model_name='scan',
            name='image',
            field=models.ImageField(upload_to=b'scans'),
        ),
    ]
