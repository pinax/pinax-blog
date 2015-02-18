# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='state',
            field=models.IntegerField(default=1, choices=[(1, 'Draft'), (2, b'Published')]),
            preserve_default=True,
        ),
    ]
