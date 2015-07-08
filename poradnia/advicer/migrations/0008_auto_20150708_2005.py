# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advicer', '0007_auto_20150520_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advice',
            name='comment',
            field=models.TextField(null=True, verbose_name='Comment', blank=True),
            preserve_default=True,
        ),
    ]