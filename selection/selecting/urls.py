from django.urls import path, include
from . import views

app_name = "selecting"
urlpatterns = [
    path("login/", include("login.urls")),
    path("", views.index, name="index"),
    path("show_series/", views.show_series, name="show_series"),
    path("show_unit_selection/<str:series>", views.show_unit_selection , name="show_unit_selection"),
    path("show_components/<int:unit>", views.show_components, name="show_components"),
    path("calculatecapacity", views.calculatecapacity, name="calculatecapacity"),
    path("inverter_compressor/<int:comp>", views.inverter_compressor, name="inverter_compressor"),
    path("set_default_airflow/<int:unit>", views.set_default_airflow, name="set_default_airflow"),
    path("add_calculation_to_cart/<int:cal_id>", views.add_calculation_to_cart, name="add_calculation_to_cart"),

    # Cart Session
    path("cart/", views.show_cart, name="show_cart"),
]