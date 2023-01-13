from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Condenser(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    # Dry coil coefficients
    dry_coefficient = ArrayField(models.FloatField(), size = 3, null=True)
 
    def __str__(self):
        return f"{self.model.upper()}"

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
        return f"{self.model.upper()}"


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
        return f"{self.model.upper()}({self.refrigerant.upper()})"


class Fan(models.Model):
    model = models.CharField(max_length=32)

    rpm_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    power_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    current_coefficient = ArrayField(models.FloatField(), size = 9, null=True)

    def __str__(self):
        return f"{self.model.upper()}"


class FlowOrientation(models.Model):
    flow_orientaion = models.CharField(max_length = 16)

    def __str__(self):
        return f"{self.flow_orientaion.upper()}"


class Unit(models.Model):
    model = models.CharField(max_length = 16, blank = True)
    flow_direction = models.ManyToManyField(FlowOrientation, blank=True, related_name="unit")
    evaporator = models.ForeignKey(Evaporator, null = True, on_delete = models.CASCADE, related_name = "evaporator")

    compressor = models.ForeignKey(Compressor, null = True, on_delete = models.CASCADE, related_name = "compressor")
    condenser = models.ManyToManyField(Condenser, blank = True, related_name = "condenser")
    fan = models.ForeignKey(Fan, null = True, on_delete = models.CASCADE, related_name = "fan")
    number_of_fan = models.PositiveIntegerField(default=1, validators = [MinValueValidator(1), MaxValueValidator(10)])
    default_airflow = models.FloatField(default=0)
    g4_static_coefficient = ArrayField(models.FloatField(), size = 3, null = True)
    f7_static_coefficient = ArrayField(models.FloatField(), size = 3, null = True)

    def __str__(self):
        return f"{self.model.upper()}"
