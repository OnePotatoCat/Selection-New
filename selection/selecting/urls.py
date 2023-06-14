from django.urls import path, include
from . import views

app_name = "selecting"
urlpatterns = [
    path("login/", include("login.urls")),
    path("", views.index, name="index"),
    # path("/<str:series>", views.unit_selection, name="unit_selection2"),
    path("/<str:series>", views.unit_selection, name="unit_selection"),
    # path("selection", views.unit_selection, name="selection"),
    # path("calculate_selection", views.calculate_selection, name="calculate_selection"),
    # path("newselection", views.newselection, name="newselection"),
    path("show_series/", views.show_product_series, name="show_series"),
    path("show_components/<int:unit>", views.show_components, name="show_components"),
    path("calculatecapacity", views.calculatecapacity, name="calculatecapacity"),
    path("inverter_compressor/<int:comp>", views.inverter_compressor, name="inverter_compressor"),
    path("set_default_airflow/<int:unit", views.set_default_airflow, name="set_default_airflow")
]