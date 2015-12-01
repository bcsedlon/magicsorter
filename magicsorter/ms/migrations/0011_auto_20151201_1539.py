# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms', '0010_scan_outbox'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scan',
            old_name='order',
            new_name='position',
        ),
        migrations.AlterField(
            model_name='card',
            name='name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
