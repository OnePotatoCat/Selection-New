from django.urls import path
from . import views

app_name = "selecting"
urlpatterns = [
    path("", views.index, name="index"),
    path("selection", views.unit_selection, name="selection"),
    path("calculate_selection", views.calculate_selection, name="calculate_selection"),
    path("newselection", views.newselection, name="newselection"),
    path("showcomponents/<int:unit>", views.showcomponents, name="showcomponents"),
    path("calculatecapacity", views.calculatecapacity, name="calculatecapacity")
]