from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from .models import Unit, Condenser

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

    def __init__(self, condensers):
        super(Calculation_Form, self).__init__()
        self.fields['condenser_Model'] = forms.ChoiceField(choices = condensers, 
            widget = forms.Select(attrs={
            'style': 'width:200px;',
            'class':'form-control'
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


def unit_selection(request):
    units = Unit.objects.all()
    if request.method == "GET":
        return render(request, "selecting/selection.html", {
            "units" : units
        })
    else:
        unit = Unit.objects.get(pk=int(request.POST["unit"]))
        unit_id = unit.id

        compressor = unit.compressor
        fan = unit.fan
        condensers = unit.condenser.all()
        condensers = [(condenser.id, condenser.model.upper()) for condenser in condensers]
        # print(condensers)
        # Compressor.main()
        # Evaporator.main()
        # Condenser.main()
        Fan.main()
        Unit.main()
        return render(request, "selecting/selection.html", {
            "units" : units,
            "sel_unit" : unit_id,
            "compressor" : compressor,
            "fan" : fan,
            "calc_form" : Calculation_Form(condensers)
        })


def calculate_selection(request):
    if request.method == "POST":

        return render(request, "selecting/calculation_selection.html", {
            "form" : NewUnitSelectionForm()
        })