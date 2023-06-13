from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django import forms
from .models import Series, Unit, Compressor, Condenser
from django.contrib.auth import authenticate, logout
from django.contrib import messages

import json
import Selection
from . import Selection as sel
from .Compressor import Compressor_Cal
from .Evaporator import Evaporator_Cal
from .Condenser import Condenser_Cal
from .Fan import Fan_Cal
from .Unit import Unit_Cal

CONDENSER_MODEL = []

# Create your views here.
class NewTaskForm(forms.Form):
    temp = forms.FloatField(label="Return Air Temperature", min_value=5.0, max_value=40.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '24',
            'style': 'width:200px;',
            'class':'form-control'
        }))
    rh = forms.FloatField(label = "Return Air Relative Humidity", min_value=10, max_value=99.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '50',
            'style': 'width:200px;',
            'class':'form-control'
        }))
    airflow = forms.FloatField(label = "Airflow Rate, m3/hr", min_value=4000, max_value=8000,
        widget=forms.NumberInput(attrs = {
            'placeholder': '6650',
            'style': 'width:200px;',
            'class':'form-control'
        }))


class Calculation_Form(forms.Form):

    compressor = forms.ChoiceField(choices = [])
    fan = forms.ChoiceField(choices = [])
    condenser = forms.ChoiceField(choices = [])

    def __init__(self, compressor, fan, condensers):
        super(Calculation_Form, self).__init__()
        self.fields['compressor'] = forms.ChoiceField(choices = compressor, 
            widget = forms.Select(attrs={
            'style': 'width:200px;',
            'class': 'form-control'
        }))

        self.fields['fan'] = forms.ChoiceField(choices = fan, 
            widget = forms.Select(attrs={
            'style': 'width:200px;',
            'class': 'form-control'
        }))

        self.fields['condenser'] = forms.ChoiceField(choices = condensers, 
            widget = forms.Select(attrs={
            'style': 'width:200px;',
            'class': 'form-control'
        }))
        
    temp = forms.FloatField(label="Return Air Temperature", min_value=5.0, max_value=40.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '24',
            'style': 'width:200px;',
            'class':'form-control'
        }))

    rh = forms.FloatField(label = "Return Air Relative Humidity", min_value=10, max_value=99.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '50',
            'style': 'width:200px;',
            'class':'form-control'
        }))

    airflow = forms.FloatField(label = "Airflow Rate, m3/hr", min_value=4000, max_value=8000,
        widget=forms.NumberInput(attrs = {
            'placeholder': '6650',
            'style': 'width:200px;',
            'class':'form-control'
        }))

    esp = forms.FloatField(label = "External Static Pressure, Pa", min_value=10, max_value=400,
        widget=forms.NumberInput(attrs = {
            'placeholder': '50',
            'style': 'width:200px;',
            'class':'form-control'
        }))


class NewUnitSelectionForm(forms.Form):
    def __init__(self):
        super(NewUnitSelectionForm, self).__init__()
        units = Unit.objects.all()
        ids, models = units.values_list('id').order_by('id'), units.values_list('model').order_by('id')
        id_model_pairs = [(ids[i][0], models[i][0].upper()) for i in range(0, len(ids))]
        self.fields['selections'] = forms.ChoiceField(
            choices = [(pair[0], pair[1]) for pair in id_model_pairs])


# ------------------------------------ #
#          View Functions 
# ------------------------------------ #
def index(request):
    # units = Unit.objects.all()
    return render(request, "selecting/layout.html", {
        "username" : request.session["user"]["first_name"]
    })

def newselection(request):
    units = Unit.objects.all()
    return render(request, "selecting/newselection.html", {
        "username" : request.user.get_short_name(),
        "units" : units
    })

def show_product_series(request):
    # TODO Get Series available from Database
    series_names= Series.objects.all()
    series_dict = {}
    for name in series_names:
        series_dict[name.id] = name.series_name.upper()
    
    # print(series_dict)
    # jsonData = json.dumps(series_dict)
    return JsonResponse(series_dict)


def show_components(request, unit):
    data = {}
    unit = Unit.objects.get(pk=int(unit))
    
    comp = unit.compressor
    comp_dict = {}
    comp_dict[comp.id] = comp.model.upper()
    data["compressor"] = comp_dict

    fan = unit.fan
    fan_dict = {}
    fan_dict[fan.id] = fan.model.upper()
    data["fan"] = fan_dict

    condensers = unit.condenser.all()
    cond_dict = {}
    for condenser in condensers:
        cond_dict[condenser.id] = condenser.model.upper()
    data["condenser"] = cond_dict

    default_airflow = unit.default_airflow
    data["default_airflow"] = default_airflow

    jsonData = json.dumps(data)
    return HttpResponse(jsonData)


def set_default_airflow(request, unit):
    unit = Unit.objects.get(pk=int(unit))
    return JsonResponse({"airflow": unit.default_airflow})

def inverter_compressor(request, comp):
    compressor = Compressor.objects.get(pk=int(comp))
    return JsonResponse({"inverter": compressor.inverter})


def calculatecapacity(request):
    if request.method =="POST":
        form = request.POST
        unit_id = int(form["unit"])
        evap_id = Unit.objects.get(pk=int(unit_id)).evaporator.id
        comp_id = int(form["comp"])
        fan_id = int(form["fan"])
        cond_id = int(form["cond"])
        inlet_temp = float(form["temp"])
        rh = float(form["rh"])
        airflow = float(form["airflow"])
        esp = float(form["esp"])
        amb_temp = float(form["amb_temp"])
        filter_type = form["filter"].lower()


        if (form["comp_sp"] != ''):
            comp_speed = float(form["comp_sp"])
        else:
            comp_speed = float(0)

        result = sel.main(unit_id, evap_id, cond_id, comp_id, fan_id, inlet_temp, rh, airflow, esp, amb_temp, comp_speed, filter_type)
        print(result)
        # jsonResult= json.dumps(result)
        # print(jsonResult)
        return JsonResponse(result)