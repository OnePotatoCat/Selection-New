from django.contrib import admin
from .models import Unit, Evaporator, Condenser, Compressor, Fan, FlowOrientation

# Register your models here.
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "model")
    filter_horizontal = ("flow_direction", "condenser",)

class EvaporatorAdmin(admin.ModelAdmin):
    list_display =("id", "model")

admin.site.register(Unit, UnitAdmin)
admin.site.register(Evaporator, EvaporatorAdmin)
admin.site.register(Condenser)
admin.site.register(Compressor)
admin.site.register(Fan)
admin.site.register(FlowOrientation)