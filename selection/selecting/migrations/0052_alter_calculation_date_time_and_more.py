# Generated by Django 4.1.5 on 2023-11-03 04:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0051_alter_calculation_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 3, 12, 54, 8, 661111)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 3, 12, 54, 8, 664109)),
        ),
    ]
