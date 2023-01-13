from django.contrib import admin
from .models import Unit, Evaporator, Condenser, Compressor, Fan, FlowOrientation

# Register your models here.
class UnitAdmin(admin.ModelAdmin):
    filter_horizontal = ("flow_direction", "condenser",)

admin.site.register(Unit,UnitAdmin)
admin.site.register(Evaporator)
admin.site.register(Condenser)
admin.site.register(Compressor)
admin.site.register(Fan)
admin.site.register(FlowOrientation)