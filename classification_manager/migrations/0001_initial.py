# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-13 12:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('permission_admin', '0001_initial'),
        ('searcher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobQueue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('job_key', models.CharField(max_length=200)),
                ('run_status', models.CharField(max_length=200)),
                ('run_started', models.DateTimeField(blank=True, null=True)),
                ('run_completed', models.DateTimeField(blank=True, null=True)),
                ('total_processed', models.CharField(max_length=200)),
                ('total_positive', models.CharField(max_length=200)),
                ('total_negative', models.CharField(max_length=200)),
                ('total_documents', models.CharField(max_length=200)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='permission_admin.Dataset')),
            ],
        ),
        migrations.CreateModel(
            name='ModelClassification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('run_description', models.CharField(max_length=200)),
                ('run_status', models.CharField(max_length=200)),
                ('run_started', models.DateTimeField()),
                ('run_completed', models.DateTimeField(blank=True, null=True)),
                ('search', models.TextField(blank=True, null=True)),
                ('fields', models.CharField(max_length=200)),
                ('clf_arch', models.TextField(blank=True, null=True)),
                ('score', models.TextField(blank=True, null=True)),
                ('tag_label', models.CharField(max_length=200)),
                ('train_summary', models.CharField(max_length=200)),
                ('model_key', models.CharField(max_length=200)),
                ('dataset_pk', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='jobqueue',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classification_manager.ModelClassification'),
        ),
        migrations.AddField(
            model_name='jobqueue',
            name='search',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='searcher.Search'),
        ),
    ]
