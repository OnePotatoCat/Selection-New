from django.urls import path
from . import views

app_name = "selecting"
urlpatterns = [
    path("", views.index, name="index"),
    path("selection", views.selection, name="index")
]