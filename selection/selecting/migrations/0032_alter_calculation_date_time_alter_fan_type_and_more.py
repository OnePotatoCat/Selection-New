# Generated by Django 4.1.5 on 2023-06-26 02:27

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0031_fan_type_alter_calculation_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 10, 27, 41, 638037)),
        ),
        migrations.AlterField(
            model_name='fan',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'AC'), (2, 'EC'), (3, 'DC'), (4, 'BD')], validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 10, 27, 41, 638037)),
        ),
    ]
