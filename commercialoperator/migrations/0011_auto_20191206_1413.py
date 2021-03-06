# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-12-06 06:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0010_auto_20191003_1519'),
    ]

    operations = [ 
        migrations.AlterField(
            model_name='communicationslogentry',
            name='type',
            field=models.CharField(choices=[('email', 'Email'), ('phone', 'Phone Call'), ('mail', 'Mail'), ('person', 'In Person'), ('onhold', 'On Hold'), ('onhold_remove', 'Remove On Hold'), ('with_qaofficer', 'With QA Officer'), ('with_qaofficer_completed', 'QA Officer Completed'), ('referral_complete', 'Referral Completed')], default='email', max_length=35),
        ),
    ]
