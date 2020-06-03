# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-06-03 05:23
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0021_auto_20200515_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationfeediscount',
            name='discount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='application_discount',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='licence_discount',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='proposaltype',
            name='name',
            field=models.CharField(choices=[('T Class', 'T Class')], default='T Class', max_length=64, verbose_name='Application name (eg. T Class, Filming, Event, E Class)'),
        ),
    ]