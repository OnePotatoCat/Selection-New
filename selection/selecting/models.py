from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField
import datetime

date_time_format = "%Y %b %d %H:%M"    

# ---------------------------------------- #
#        DX Components Database
# ---------------------------------------- #
class Condenser(models.Model):
    model = models.CharField(max_length=16)
    airflow_m3hr = models.FloatField()
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    # Dry coil coefficients
    dry_coefficient = ArrayField(models.FloatField(), size = 3, null=True)
    
    def get_model_name(self):
        model_name = self.model.split("-")
        return model_name[0].upper()
    
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

    # Starting Dewpoint
    starting_dewpoint = ArrayField(models.FloatField(), size= 7, null=-True)

    def __str__(self):
        return f"{self.model.upper()}"


class Compressor(models.Model):
    model = models.CharField(max_length=16)
    hp = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    refrigerant = models.CharField(max_length=10)
    inverter = models.BooleanField()
    voltage = models.IntegerField()
    subcool = models.FloatField()
    superheat = models.FloatField()
    volume = models.FloatField()
    evap_temp_limit = models.FloatField()
    capacity_factor = models.FloatField()
    capacity_coefficient = ArrayField(models.FloatField(), size = 24, null=True)
    power_coefficient = ArrayField(models.FloatField(), size = 24, null=True)
    current_coefficient = ArrayField(models.FloatField(), size = 24, null=True)
    massflow_coefficient = ArrayField(models.FloatField(), size = 24, null=True)

    def __str__(self):
        return f"{self.model.upper()}({self.refrigerant.upper()})"


class MotorType(models.Model):
    type = models.CharField(max_length=2, blank=True)

    def get_dynamic_choices(self):
        choices = [(motor_type.id, motor_type.type) for motor_type in MotorType.objects.all()]
        return choices

    def __str__(self):
        return f"{self.type.upper()}"


class Fan(models.Model):
    model = models.CharField(max_length=32)
    type = models.PositiveIntegerField(validators=[MaxValueValidator(10)], choices=MotorType().get_dynamic_choices())
    size = models.PositiveIntegerField(validators=[MaxValueValidator(1000)])
    rpm_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    power_coefficient = ArrayField(models.FloatField(), size = 9, null=True)
    current_coefficient = ArrayField(models.FloatField(), size = 9, null=True)

    def __str__(self):
        return f"{self.model.upper()}"


class FlowOrientation(models.Model):
    flow_orientaion = models.CharField(max_length = 40)
    discharge_orientation = models.CharField(max_length=1, default="U")

    def __str__(self):
        return f"{self.flow_orientaion.upper()}"


class Series(models.Model):
    arrange_id = models.PositiveIntegerField(unique=True)
    series_name = models.CharField(max_length=10, blank = False)
    image = models.ImageField(upload_to='images/', null = True)

    def __str__(self):
        return f"{self.series_name.upper()}"


# ---------------------------------------- #
# Chill Water Database
# ---------------------------------------- #
class ChillwaterCoil(models.Model):
    model = models.CharField(max_length=16)
    area_surface = models.FloatField()
    area_frontal = models.FloatField()
    min_airflow = models.FloatField()
    max_airflow = models.FloatField()

    # Dry coil coefficients
    udry_model = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)

    # Wet coil coefficients
    uwet_model = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)

    # Flowrate(Dry) model
    mdry_model = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)

    # Flowrate(Wet) model
    mwet_model = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)
    
    # Starting Dewpoint
    starting_dewpoint = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)
    
    # Pressure Drop model
    dp_model = models.FileField(upload_to="cwmodel", default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.model.upper()}"


# ---------------------------------------- #
#  Bootstrap Unit Database
# ---------------------------------------- #
class Unit(models.Model):
    series = models.ForeignKey(Series, null = True, on_delete = models.RESTRICT, related_name = "series")
    arrange_id = models.PositiveIntegerField()
    model = models.CharField(max_length = 16, blank = True)
    length = models.PositiveIntegerField(default=100, validators = [MinValueValidator(50), MaxValueValidator(4000)])
    depth = models.PositiveIntegerField(default=100, validators = [MinValueValidator(50), MaxValueValidator(4000)])
    height = models.PositiveIntegerField(default=100, validators = [MinValueValidator(50), MaxValueValidator(4000)])
    power_supply = models.CharField(max_length = 13, default="400V-3ph-50Hz")
    flow_direction = models.ManyToManyField(FlowOrientation, blank=True, related_name="flow")

    # DX Components
    evaporator = models.ForeignKey(Evaporator, blank=True, null = True, on_delete = models.RESTRICT, related_name = "evaporator")
    compressor = models.ForeignKey(Compressor, blank=True, null = True, on_delete = models.RESTRICT, related_name = "compressor")
    default_comp_speed = models.PositiveIntegerField(default=100, validators = [MinValueValidator(30), MaxValueValidator(120)])
    number_of_compressor = models.PositiveIntegerField(default=1, validators = [MinValueValidator(1), MaxValueValidator(3)])
    condenser = models.ManyToManyField(Condenser, blank = True, related_name = "condenser")
    # CW Component
    cw_coil = models.ForeignKey(ChillwaterCoil, blank=True, null=True, on_delete = models.RESTRICT, related_name = "cw_coil")

    # Fan and Statics Pressure
    fan = models.ForeignKey(Fan, null = True, on_delete = models.RESTRICT, related_name = "fan")
    number_of_fan = models.PositiveIntegerField(default=1, validators = [MinValueValidator(1), MaxValueValidator(10)])
    default_airflow = models.FloatField(default=0)
    g4_static_coefficient = ArrayField(models.FloatField(), size = 3, null = True)
    f7_static_coefficient = ArrayField(models.FloatField(), size = 3, null = True)

    def __str__(self):
        return f"{self.model.upper()}"


# ---------------------------------------- #
#  Calculation, Cart and History Database
# ---------------------------------------- #
class Calculation(models.Model):
    add_to_cart = models.BooleanField()
    date_time = models.DateTimeField(default=datetime.datetime.now())
    model = models.ForeignKey(Unit, on_delete=models.RESTRICT, related_name="unit")
    flow_orientaion = models.ForeignKey(FlowOrientation, on_delete=models.RESTRICT)
    cond = models.ForeignKey(Condenser, on_delete=models.RESTRICT, related_name="cond")
    inlet_temp = models.FloatField()
    inlet_rh = models.FloatField()
    airflow = models.PositiveIntegerField()
    esp = models.PositiveIntegerField()
    amb_temp = models.FloatField()
    filter = models.CharField(max_length=3)
    comp = models.ForeignKey(Compressor, on_delete=models.RESTRICT, related_name="comp")
    comp_spd = models.PositiveIntegerField()
    total_cap = models.FloatField()
    sen_cap = models.FloatField()
    heat_rejection = models.FloatField()
    fan_power = models.FloatField()
    fan_rpm = models.PositiveIntegerField()
    tsp = models.IntegerField()
    t_evap = models.FloatField()
    t_cond = models.FloatField()
    off_temp = models.FloatField()
    off_rh = models.FloatField()
    outlet_temp= models.FloatField()
    outlet_rh = models.FloatField()

    def __str__(self):
        return f"{self.model}  {self.date_time}  {self.sen_cap}"
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    calculation = models.ForeignKey(Calculation, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.user}  {self.calculation}"
    
class History(models.Model):
    STATUS_CHOICES = [
        ("Del", "Deleted"),
        ("Gen", "Generated")
    ]
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    calculation = models.ForeignKey(Calculation, on_delete=models.RESTRICT)
    generated_date_time = models.DateTimeField(default=datetime.datetime.now())
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES)

    def get_condenser(self):
        condenser = self.calculation.cond.model.split("-")
        return condenser[0].upper()

    def __str__(self):
        return f"{self.user} {self.get_status_display()} {self.calculation}  {self.generated_date_time.strftime(date_time_format)}"