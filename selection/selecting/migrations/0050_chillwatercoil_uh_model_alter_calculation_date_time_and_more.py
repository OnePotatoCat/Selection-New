# Generated by Django 4.1.5 on 2023-11-03 04:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0049_chillwatercoil_alter_calculation_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chillwatercoil',
            name='uh_model',
            field=models.BinaryField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 3, 12, 44, 58, 802715)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 3, 12, 44, 58, 804296)),
        ),
    ]
