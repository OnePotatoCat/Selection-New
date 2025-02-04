# Generated by Django 4.1.5 on 2023-06-26 09:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0034_calculation_heat_rejection_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='status',
            field=models.CharField(choices=[('Del', 'Deleted'), ('Gen', 'Generated')], default='Del', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calculation',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 17, 58, 46, 600327)),
        ),
        migrations.AlterField(
            model_name='history',
            name='generated_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 17, 58, 46, 601500)),
        ),
    ]
