from django.urls import path
from . import views

app_name = "selecting"
urlpatterns = [
    path("", views.index, name="newselection"),
    # path("selection", views.unit_selection, name="selection"),
    # path("calculate_selection", views.calculate_selection, name="calculate_selection"),
    # path("newselection", views.newselection, name="newselection"),
    path("show_components/<int:unit>", views.show_components, name="show_components"),
    path("calculatecapacity", views.calculatecapacity, name="calculatecapacity"),
    path("inverter_compressor/<int:comp>", views.inverter_compressor, name="inverter_compressor"),
    path("set_default_airflow/<int:unit", views.set_default_airflow, name="set_default_airflow")
]