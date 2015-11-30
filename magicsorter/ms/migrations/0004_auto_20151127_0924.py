# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0003_auto_20151127_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scan',
            name='order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
