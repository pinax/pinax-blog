# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedHit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_data', models.TextField()),
                ('created', models.DateTimeField(default=timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_path', models.ImageField(upload_to=b'images/%Y/%m/%d')),
                ('url', models.CharField(max_length=150, blank=True)),
                ('timestamp', models.DateTimeField(default=timezone.now, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section', models.IntegerField(choices=[(1, 'all'), (2, b'Release Notes')])),
                ('title', models.CharField(max_length=90)),
                ('slug', models.SlugField()),
                ('markup', models.CharField(max_length=25, choices=[('markdown', 'Markdown'), ('creole', 'Creole')])),
                ('teaser_html', models.TextField(editable=False)),
                ('content_html', models.TextField(editable=False)),
                ('description', models.TextField(blank=True)),
                ('tweet_text', models.CharField(max_length=140, editable=False)),
                ('created', models.DateTimeField(default=timezone.now, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('published', models.DateTimeField(null=True, editable=False, blank=True)),
                ('secret_key', models.CharField(help_text=b'allows url for sharing unpublished posts to unauthenticated users', unique=True, max_length=8, blank=True)),
                ('view_count', models.IntegerField(default=0, editable=False)),
                ('author', models.ForeignKey(related_name='posts', to=settings.AUTH_USER_MODEL)),
                ('primary_image', models.ForeignKey(related_name='+', blank=True, to='blog.Image', null=True)),
            ],
            options={
                'ordering': ('-published',),
                'get_latest_by': 'published',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReviewComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('review_text', models.TextField()),
                ('timestamp', models.DateTimeField(default=timezone.now)),
                ('addressed', models.BooleanField(default=False)),
                ('post', models.ForeignKey(related_name='review_comments', to='blog.Post')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=90)),
                ('teaser', models.TextField()),
                ('content', models.TextField()),
                ('updated', models.DateTimeField(default=timezone.now)),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('view_count', models.IntegerField(default=0, editable=False)),
                ('author', models.ForeignKey(related_name='revisions', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(related_name='revisions', to='blog.Post')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='image',
            name='post',
            field=models.ForeignKey(related_name='images', to='blog.Post'),
            preserve_default=True,
        ),
    ]
