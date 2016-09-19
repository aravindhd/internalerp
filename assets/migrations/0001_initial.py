# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-14 11:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='assetCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'permissions': (('view_asset_categories', 'View Asset Categories'),),
            },
        ),
        migrations.CreateModel(
            name='assets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assetId', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('serialNumber', models.CharField(max_length=100)),
                ('manufacturer', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[(b'INSTOCK', b'In-Stock'), (b'ASSIGNED', b'Assigned'), (b'LOST', b'Lost'), (b'STOLEN', b'Stolen'), (b'MISSING', b'Missing'), (b'INSERVICE', b'In-Service'), (b'REPAIR', b'Repair')], default=b'INSTOCK', max_length=25)),
                ('assignmentCategory', models.CharField(choices=[(b'GENERAL', b'General'), (b'EMPLOYEE', b'Employee'), (b'MANAGER', b'Manager'), (b'SHARED', b'Shared')], default=b'GENERAL', max_length=25)),
                ('creationTimestamp', models.DateTimeField(auto_now_add=True)),
                ('lastUpdateTimestamp', models.DateTimeField(auto_now=True)),
                ('assignedTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.EmployeesDirectory')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.assetCategories')),
            ],
            options={
                'ordering': ['assetId', 'category', 'name'],
                'permissions': (('view_assets', 'View Assets'),),
            },
        ),
    ]
