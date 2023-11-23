from django.contrib import admin
from .models import Series, Calculation, Cart, History, Unit, Evaporator, Condenser, ChillwaterCoil, Compressor, MotorType, Fan, FlowOrientation

# Register your models here.
class UnitAdmin(admin.ModelAdmin):
    list_display = ("arrange_id", "series", "model")
    filter_horizontal = ("flow_direction", "condenser",)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ("arrange_id", "series_name")

class EvaporatorAdmin(admin.ModelAdmin):
    list_display =("id", "model",)

class CalculationAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "date_time", )

class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "calculation")

class HistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "calculation", "generated_date_time")


admin.site.register(Unit, UnitAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Calculation, CalculationAdmin)
admin.site.register(Evaporator, EvaporatorAdmin)
admin.site.register(ChillwaterCoil)
admin.site.register(Condenser)
admin.site.register(Compressor)
admin.site.register(MotorType)
admin.site.register(Fan)
admin.site.register(FlowOrientation)