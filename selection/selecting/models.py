from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Condenser(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    # Dry coil coefficients
    dry_coefficient = ArrayField(models.FloatField(), size = 3, null=True)
 
    def __str__(self):
        return f"{self.model.upper()}, surface area: {self.area_surface}, frontal area: {self.area_frontal}"

class Evaporator(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    min_airflow = models.FloatField()
    max_airflow = models.FloatField()
    # Dry coil coefficients
    dry_coefficient = ArrayField(models.FloatField(), size = 3, null=True)

    # Wet coil coefficients
    wet_coefficient = ArrayField(models.FloatField(), size = 9, null=True)


    def __str__(self):
        return f"{self.model.upper()}, surface area: {self.area_surface}, frontal area: {self.area_frontal}"


class Compressor(models.Model):
    model = models.CharField(max_length=16)
    refrigerant = models.CharField(max_length=10)
    voltage = models.IntegerField()
    
    subcool = models.FloatField()
    superheat = models.FloatField()
    volume = models.FloatField()

    capacity_coefficient = ArrayField(models.FloatField(), size = 10, null=True)
    power_coefficient = ArrayField(models.FloatField(), size = 10, null=True)
    supply_coefficient = ArrayField(models.FloatField(), size = 10, null=True)
    massflow_coefficient = ArrayField(models.FloatField(), size = 10, null=True)


    def __str__(self):
        return f"{self.model.upper()}, refrigerant: {self.refrigerant.upper()}"


class Fan(models.Model):
    model = models.CharField(max_length=32)

    rpm_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    power_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    current_coefficient = ArrayField(models.FloatField(), size = 9, null=True)


    def __str__(self):
        return f"{self.model.upper()}"