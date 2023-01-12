from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Condenser(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    # Dry coil coefficients
    dry_coef0 = models.FloatField()
    dry_coef1 = models.FloatField()
    dry_coef2 = models.FloatField()
 
    def __str__(self):
        return f"{self.model.upper()}, surface area: ({self.area_surface}, frontal area: ({self.area_frontal})"

class Evaporator(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    min_airflow = models.FloatField()
    max_airflow = models.FloatField()
    # Dry coil coefficients
    dry_c0 = models.FloatField()
    dry_c1 = models.FloatField()
    dry_c2 = models.FloatField()
    # Wet coil coefficients
    wet_c0 = models.FloatField()
    wet_c1 = models.FloatField()
    wet_c2 = models.FloatField()
    wet_c3 = models.FloatField()
    wet_c4 = models.FloatField()
    wet_c5 = models.FloatField()
    wet_c6 = models.FloatField()
    wet_c7 = models.FloatField()
    wet_c8 = models.FloatField()

    tags = ArrayField(models.CharField(max_length=200, blank=True), size= 3)

    def __str__(self):
        return f"{self.model.upper()}, surface area: ({self.area_surface}, frontal area: ({self.area_frontal})"