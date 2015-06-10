# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


def seed_sections(apps, schema_editor):
    Section = apps.get_model("blog", "Section")
    db_alias = schema_editor.connection.alias
    for section in settings.PINAX_BLOG_SECTIONS:
        Section.objects.using(db_alias).create(slug=section[0], name=section[1])


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
        migrations.RunPython(
            code=seed_sections,
        ),
        migrations.AlterField(
            model_name='post',
            name='section',
            field=models.ForeignKey(to='blog.Section'),
            preserve_default=True,
        ),
    ]
