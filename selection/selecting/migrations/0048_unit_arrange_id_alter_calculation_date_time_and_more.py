# Generated by Django 4.1.5 on 2023-10-04 07:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0047_compressor_capacity_factor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='arrange_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 4, 15, 26, 36, 107859)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 4, 15, 26, 36, 107859)),
        ),
    ]
