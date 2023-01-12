from django.shortcuts import render
from django import forms
import sys
sys.path.append('../parentdirectory')
import Selection
import Unit

# Create your views here.

class NewTaskForm(forms.Form):
    temp = forms.FloatField(label="Return Air Temperature", min_value=5.0, max_value=40.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '24',
            'style': 'width:200px;',
            'class':'form-control'
        }))
    rh = forms.FloatField(label="Return Air Relative Humidity", min_value=10, max_value=99.0,
        widget=forms.NumberInput(attrs = {
            'placeholder': '50',
            'style': 'width:200px;',
            'class':'form-control'
        }))
    airflow = forms.FloatField(label="Airflow Rate", min_value=4000, max_value=8000,
        widget=forms.NumberInput(attrs = {
            'placeholder': '6650',
            'style': 'width:200px;',
            'class':'form-control'
        }))

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
