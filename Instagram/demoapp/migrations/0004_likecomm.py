# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demoapp', '0003_commentmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeComm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demoapp.CommentModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demoapp.UserModel')),
            ],
        ),
    ]
