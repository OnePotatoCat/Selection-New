from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django.template import loader
from django.template.loader import render_to_string
from django import forms
from .models import Series, Unit, Compressor, Condenser, FlowOrientation, Calculation, Cart
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages

import json
import Selection
import datetime
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
    units = Unit.objects.all()
    return render(request, "selecting/layout.html", {
        "username" :request.user.username,
        "admin" : request.user.is_staff,
        # "username" : request.session["user"]["first_name"]
        # "units" :units
    })


def show_series(request):
    series_names= Series.objects.all()
    content={"series" :series_names}

    series_dict = {}
    for name in series_names:
        series_dict[name.id] = name.series_name.upper()    

    template = loader.get_template("selecting/series_album.html")
    selection_html = template.render(content, request)
    return HttpResponse(selection_html)


def show_unit_selection(request, series):
    units = Unit.objects.filter(series = int(series))
    content = {
        "units" :units, 
        "admin": request.user.is_staff,
        }
    units_dict= {}
    for unit in units:
        units_dict[unit.id] = unit.model.upper()

    template = loader.get_template("selecting/newselection.html")
    selection_html = template.render(content, request)
    return HttpResponse(selection_html)


def show_components(request, unit):
    data = {}
    unit = Unit.objects.get(pk=int(unit))
    
    flows = unit.flow_direction.all()
    flow_dict = {}
    for flow in flows:
        flow_dict[flow.id] = flow.flow_orientaion.upper()
    data["flow"] = flow_dict

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
    return JsonResponse(data)


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
        flow_id = int(form["flow"])
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
        result["calculation id"] = ""

        if result["converged"]:
            new_calculation = Calculation(
                add_to_cart = False,
                date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                model = Unit.objects.get(pk=int(unit_id)),
                flow_orientaion = FlowOrientation.objects.get(pk=int(flow_id)),
                cond = Condenser.objects.get(pk=int(cond_id)),
                inlet_temp = inlet_temp,
                inlet_rh = rh,
                airflow = airflow,
                esp = esp,
                amb_temp = amb_temp,
                filter = filter_type,
                comp = Compressor.objects.get(pk=int(comp_id)),
                comp_spd = comp_speed,
                total_cap = result["capacity"]["Total Capacity"][0],
                sen_cap = result["capacity"]["Total Sensible Cap."][0],
                fan_power = result["fan"]["Fan Power"][0],
                fan_rpm = result["fan"]["Fan RPM"][0],
                tsp = result["fan"]["Total Static Pressure"][0],
                t_evap = result["compressor"]["Evaporating Temp."][0],
                t_cond = result["compressor"]["Condensing Temp."][0],
                off_temp = result["air"]["Off Coil Temperature"][0],
                off_rh = result["air"]["Off Coil RH"][0],
                outlet_temp = result["air"]["Outlet Temperature"][0], 
                outlet_rh = result["air"]["Outlet RH"][0],
            )

            new_calculation.save()
            result["calculation id"] = new_calculation.id

        print(result)
        return JsonResponse(result)
    

def add_calculation_to_cart(request, cal_id):
    calculation_data = Calculation.objects.get(pk=int(cal_id))
    calculation_data.add_to_cart = True
    cart = Cart(
        user = User.objects.get(pk=int(request.user.id)),
        calculation = Calculation.objects.get(pk=int(cal_id))
    )
    cart.save()
    return JsonResponse({"success": calculation_data.add_to_cart })


def show_cart(request):
    return HttpResponse(selection_html)
        