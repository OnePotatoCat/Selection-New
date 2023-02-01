from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django import forms
from .models import Unit, Condenser

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



def index(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            temp = form.cleaned_data['temp']
            rh = form.cleaned_data['rh']
            airflow =form.cleaned_data['airflow']
            converge, output = Selection.main(temp, rh, airflow)
            print(converge)
            if converge:
                return render(request, "selecting/calculated.html", {
                    "form" : form,
                    "total_cap" : round(output.total_capacity,2),
                    "sens_cap" : round(output.sensible_capacity,2),
                    "net_cap" : round(output.total_capacity - output.fan.get_power(),2),
                    "net_sen_cap" : round(output.sensible_capacity - output.fan.get_power(),2),
                    
                    "outlet_temp" : round(output.outlet_temp,1),
                    "outlet_rh" : round(output.outlet_rh,1),
                    "evap_temp" : round(output.evaporator.saturated_temp,1),
                    "cond_temp" : round(output.condenser.saturated_temp,1),
                    
                    "comp_model" : output.compressor.model.upper(),
                    "comp_power" : round(output.compressor.get_power(),0),
                    "comp_current" : round(output.compressor.get_current(),0),

                    "fan_model" : output.fan.model.upper(),
                    "fan_rpm" : round(output.fan.get_rpm(),-1),
                    "tsp" : round(output.tsp,-1),
                })
            else:
                return render(request, "selecting/failed.html", {
                    "form" : form,
                    "text" : output
                })
        else:
            return render(request, "selecting/index.html", {
                "form" : form
            })
    else:
        return render(request, "selecting/index.html", {
            "form" : NewTaskForm()
        })


def unit_selection(request, output=None):
    units = Unit.objects.all()
    if request.method == "GET":
        return render(request, "selecting/selection.html", {
            "units" : units,
            "error" : output
        })
    else:
        unit = Unit.objects.get(pk=int(request.POST["unit"]))
        unit_id = unit.id

        compressor = unit.compressor
        compressor = [(compressor.id, compressor.model.upper())]
        fan = unit.fan
        fan = [(fan.id, fan.model.upper())]
        condensers = unit.condenser.all()
        condensers = [(condenser.id, condenser.model.upper()) for condenser in condensers]

        return render(request, "selecting/selection.html", {
            "units" : units,
            "sel_unit" : unit_id,
            "compressor" : compressor,
            "fan" : fan,
            "calc_form" : Calculation_Form(compressor, fan, condensers)
        })


def calculate_selection(request):
    if request.method == "POST":
        form = request.POST
        try:
            temp = float(request.POST["temp"])
            rh = float(request.POST["rh"])
            airflow = float(request.POST["airflow"])
            esp = float(request.POST["esp"])

            compressor_id = int(request.POST["compressor"])
            fan_id = int(request.POST["fan"])
            condenser_id = int(request.POST["condenser"])
        except KeyError:
            return HttpResponseRedirect(reverse("selection")) 

        next = request.POST.get('next', '/')
        
        converge, output = sel.main(1,  1,  condenser_id,  compressor_id,  fan_id,  temp,  rh,  airflow,  esp)
        if converge:
            return render(request, "selecting/calculate_selection.html", {
                "converge" : converge,
                "form" : form,
                "total_cap" : round(output.total_capacity, 2),
                "sens_cap" : round(output.sensible_capacity, 2),
                "net_cap" : round(output.total_capacity - output.fan.get_power(),2),
                "net_sen_cap" : round(output.sensible_capacity - output.fan.get_power(),2),
                
                "outlet_temp" : round(output.outlet_temp, 1),
                "outlet_rh" : round(output.outlet_rh, 1),
                "evap_temp" : round(output.evaporator.saturated_temp, 1),
                "cond_temp" : round(output.condenser.saturated_temp, 1),
                
                "comp_model" : output.compressor.model.upper(),
                "comp_power" : round(output.compressor.get_power(), 0),
                "comp_current" : round(output.compressor.get_current(), 0),

                "fan_model" : output.fan.model.upper(),
                "fan_rpm" : round(output.fan.get_rpm(), 0),
                "tsp" : round(output.tsp, 0),
            })
        print(f"output : {output}" )
        return HttpResponseRedirect(next)


def newselection(request):
    units = Unit.objects.all()
    return render(request, "selecting/newselection.html", {
        "units" : units
    })

def showcomponents(request, unit):
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

    jsonData = json.dumps(data)
    # print(unit)
    return HttpResponse(jsonData)

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
        
        result = sel.main(unit_id, evap_id, cond_id, comp_id, fan_id, inlet_temp, rh, airflow)
        
        jsonResult= json.dumps(result)
        print(jsonResult)
        return HttpResponse(jsonResult)