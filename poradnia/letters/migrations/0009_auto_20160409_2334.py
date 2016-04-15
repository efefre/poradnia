# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-09 21:34
from __future__ import unicode_literals

from django.db import migrations, models
import letters.utils


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0008_letter_eml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='attachment',
            field=models.FileField(upload_to=letters.utils.date_random_path, verbose_name='File'),
        ),
    ]