# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(unique=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='post',
            name='markup',
            field=models.CharField(max_length=25, choices=[('markdown', 'Markdown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='section',
            field=models.ForeignKey(to='blog.Section'),
            preserve_default=True,
        ),
    ]
