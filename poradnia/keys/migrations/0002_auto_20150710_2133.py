# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created on'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='key',
            name='download_on',
            field=models.DateTimeField(null=True, verbose_name='Download on'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='key',
            name='used_on',
            field=models.DateTimeField(null=True, verbose_name='Used on'),
            preserve_default=True,
        ),
    ]