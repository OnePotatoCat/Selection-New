from django.urls import path, include
from . import views

app_name = "selecting"
urlpatterns = [
    path("login/", include("login.urls")),
    path("", views.index, name="index"),
    path("series", views.show_series, name="show_series"),
    path("show_unit_selection/<int:series>", views.show_unit_selection , name="show_unit_selection"),
    path("show_components/<int:unit>", views.show_components, name="show_components"),
    path("calculate_capacity", views.calculate_capacity, name="calculate_capacity"),
    path("inverter_compressor/<int:comp>", views.inverter_compressor, name="inverter_compressor"),
    path("set_default_airflow/<int:unit>", views.set_default_airflow, name="set_default_airflow"),
    path("add_calculation_to_cart/<int:cal_id>", views.add_calculation_to_cart, name="add_calculation_to_cart"),
    path("ac_fan_airflow/<int:unit>/<int:esp>/<str:filter>", views.ac_fan_airflow, name="ac_fan_airflow"),
    path("ac_fan_esp/<int:unit>/<int:airflow>/<str:filter>", views.ac_fan_esp, name="ac_fan_esp"),

    # CIDC/CIRC
    path("download_pdf/<str:pdf>", views.download_pdf, name="download_pdf"),

    # Cart Section
    path("cart", views.show_cart, name="show_cart"),
    path("generate_reports/<str:cal_ids>", views.generate_reports, name="generate_reports"),
    path("delete_cart_item/<str:cal_ids>", views.delete_cart_items, name="delete_cart_items"),

    # History Section
    path("history", views.show_history, name="show_history"),
]