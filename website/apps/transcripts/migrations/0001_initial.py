# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('subdomains', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.CharField(max_length=63), db_index=True)),
                ('utc_launch_time', models.DateTimeField()),
                ('memorial', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('incomplete', models.BooleanField(default=True)),
                ('main_transcript', models.CharField(max_length=20, null=True)),
                ('media_transcript', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]
