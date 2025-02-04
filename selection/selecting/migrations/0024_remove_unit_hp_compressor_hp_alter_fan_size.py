# Generated by Django 4.1.5 on 2023-06-20 02:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0023_alter_unit_hp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='hp',
        ),
        migrations.AddField(
            model_name='compressor',
            name='hp',
            field=models.PositiveIntegerField(default=5, validators=[django.core.validators.MaxValueValidator(100)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fan',
            name='size',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
    ]
