# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20150529_0405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(unique=True, max_length=150),
            preserve_default=True,
        ),
    ]
