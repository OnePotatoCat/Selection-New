# Generated by Django 4.1.5 on 2023-07-13 09:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0038_alter_calculation_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 13, 17, 15, 30, 461336)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 13, 17, 15, 30, 461336)),
        ),
    ]
