from django.contrib import admin
from .models import Evaporator, Condenser, Compressor, Fan

# Register your models here.

admin.site.register(Evaporator)
admin.site.register(Condenser)
admin.site.register(Compressor)
admin.site.register(Fan)