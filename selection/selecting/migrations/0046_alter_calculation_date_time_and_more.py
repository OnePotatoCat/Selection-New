# Generated by Django 4.1.5 on 2023-09-26 10:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0045_alter_calculation_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 26, 18, 1, 40, 763645)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 26, 18, 1, 40, 764642)),
        ),
    ]
