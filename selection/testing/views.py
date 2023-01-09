from django.http import HttpResponse
from django.shortcuts import render
import sys
sys.path.append('../parentdirectory')
import Selection

# Create your views here.

def index(request):
    return render(request, "testing/index.html")


def capacity(request):
    capacity = Selection.main(22,50, 6900)
    return render(request, "testing/capacity.html", {
        "temperature" : round(22, 1),
        "rh" : round(50, 1),
        "airflow" : round(6900, 0),
        "capacity" : round(capacity, 2)
    })
