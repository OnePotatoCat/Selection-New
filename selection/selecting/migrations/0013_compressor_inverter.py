# Generated by Django 4.1.5 on 2023-02-27 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selecting', '0012_alter_compressor_capacity_coefficient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compressor',
            name='inverter',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
