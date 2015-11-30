# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'cards')),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('withdrawn', models.BooleanField()),
                ('result0', models.FloatField()),
                ('result1', models.FloatField()),
                ('image', models.ImageField(upload_to=b'scans')),
                ('fk_card', models.ForeignKey(to='ms.Card')),
            ],
        ),
    ]
