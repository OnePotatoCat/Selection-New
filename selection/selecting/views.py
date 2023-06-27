from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse, FileResponse
from django.urls import reverse
from django.contrib.staticfiles import finders
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages

from django.core.paginator import Paginator

from django.templatetags.static import static
from django.template import loader
from django.template.loader import render_to_string
from django import forms
from .models import Series, Unit, Compressor, Condenser, FlowOrientation, MotorType, Calculation, Cart, History


import json
import os
import zipfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from svglib.svglib import svg2rlg
from PIL import Image

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

date_time_format = "%Y %b %d %H:%M"
date_time_ymd = '%Y-%m-%d %H:%M'
date_format = "%Y %b %d"
# ------------------------------------ #
#          View Functions 
# ------------------------------------ #
def index(request):
    context = {
        "username" :request.user.username,
        "admin" : request.user.is_staff,
    }
    return render(request, "selecting/layout.html", context)


def show_series(request, ):
    if request.method =='GET':
        return HttpResponseRedirect("/selecting")
    
    # if request.method == 'POST':
    seriess= Series.objects.all()
    context={"series" :seriess}
    template = loader.get_template("selecting/series_album.html")
    selection_html = template.render(context, request)
    return HttpResponse(selection_html)

        
def show_unit_selection(request, series):
    units = Unit.objects.filter(series = int(series))
    context = {
        "units" :units, 
        "admin": request.user.is_staff,
        }
    units_dict= {}
    for unit in units:
        units_dict[unit.id] = unit.model.upper()

    template = loader.get_template("selecting/newselection.html")
    selection_html = template.render(context, request)
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
        cond_dict[condenser.id] = condenser.get_model_name()
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
                date_time = datetime.datetime.now().strftime(date_time_ymd),
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
                heat_rejection = round(result["capacity"]["Total Capacity"][0]/Unit.objects.get(pk=int(unit_id)).number_of_compressor + result["compressor"]["Comp. Power"][0], 2),
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
    
    return JsonResponse({"success": calculation_data.add_to_cart,
                         "message": "Added to cart successfully" })


def show_cart(request):
    user_cart = Cart.objects.filter(user = request.user.id)
    cart_dict = {}

    for item in user_cart:
        net_total_cap = round(item.calculation.total_cap - item.calculation.fan_power, 1)
        net_sen_cap = round(item.calculation.sen_cap - item.calculation.fan_power, 1)

        cart_dict[str(item.id)] = {
            "model"         : f"{item.calculation.model} - {item.calculation.cond}",
            "total_cap"     : f"{round(item.calculation.total_cap,1)} kW",
            "sen_cap"       : f"{round(item.calculation.sen_cap,1)} kW",
            "net_total_cap" : f"{net_total_cap} kW",
            "net_sen_cap"   : f"{net_sen_cap} kW",
            "airflow"       : f"{item.calculation.airflow} m3/hr",
            "inlet_temp"    : f"{item.calculation.inlet_temp} °C", 
            "inlet_rh"      : f"{item.calculation.inlet_rh} %",
            "outlet_temp"   : f"{item.calculation.outlet_temp} °C", 
            "outlet_rh"     : f"{item.calculation.outlet_rh} %",
            "filter"        : f"{item.calculation.filter.upper()}",
            "datetime"      : f"{item.calculation.date_time.strftime(date_time_format)}"
        }

    context = {
        "cart": cart_dict, 
        "admin": request.user.is_staff,
        }
    
    template = loader.get_template("selecting/cart.html")
    cart_html = template.render(context, request)
    return HttpResponse(cart_html)

def generate_reports(request, cal_ids):
    pdfs_directory = os.path.join("selecting/reports/pdf", str(request.user.id))
    os.makedirs(pdfs_directory, exist_ok=True)
    for filename in os.listdir(pdfs_directory):
        file_path = os.path.join(pdfs_directory, filename)
        os.remove(file_path)

    zip_directory = os.path.join("selecting/reports/zip", str(request.user.id))
    os.makedirs(zip_directory, exist_ok=True)
    for filename in os.listdir(zip_directory):
        file_path = os.path.join(zip_directory, filename)
        os.remove(file_path)
    
    ids = cal_ids.split(",")
    for id in ids:
        cart = Cart.objects.get(pk=int(id))
        filename = f'{cart.id}_{cart.calculation.model}-{cart.calculation.cond}.pdf'
        file_path = os.path.join(pdfs_directory, filename)
        history = add_to_history(cart, "Gen")
        generate_pdf(file_path, history)
        cart.delete()

    zip_file_path = os.path.join(zip_directory, "generated_pdfs.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for filename in os.listdir(pdfs_directory):
            file_path = os.path.join(pdfs_directory, filename)
            zip_file.write(file_path, arcname = filename)
    
    response = FileResponse(open(zip_file_path, 'rb'), content_type='application/zip', as_attachment=True)
    response['Content-Disposition'] = 'attachment; filename = "generated_pdfs.zip'
    response['Content-Length'] = os.path.getsize(zip_file_path)
    return response


def delete_cart_items(request, cal_ids):
    ids = cal_ids.split(",")
    for id in ids:
        cart = Cart.objects.get(pk=int(id))
        history = add_to_history(cart, "Del")
        cart.delete()
    return show_cart(request)


def add_to_history(cart, status):
    history = History(
            user = User.objects.get(pk=int(cart.user.id)),
            calculation = Calculation.objects.get(pk=int(cart.calculation.id)),
            generated_date_time = datetime.datetime.now().strftime(date_time_ymd),
            status = status
        )
    history.save()
    return history


def show_history(request):
    history_list = History.objects.filter(user = request.user.id).order_by('generated_date_time').reverse()
    paginator = Paginator(history_list, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_number = 1
        page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj,
               'page_list': list(paginator.get_elided_page_range(number = page_number, on_each_side=2, on_ends=2))}

    template = loader.get_template("selecting/history.html")
    historyt_html = template.render(context, request)
    return HttpResponse(historyt_html)
    # print(context)
    # print(list(paginator.get_elided_page_range(number = page_number, on_each_side=2, on_ends=2)))
    # print(page_obj.object_list[0].calculation.model)
    

def generate_pdf(file_path, history):
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
    hist = History.objects.get(pk=int(history.id))

    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    padding = 20

    title = 'Product Selection Sheet'
    date_time = history.generated_date_time

    bar_height = 45
    logo_path = finders.find('selecting/logo_report.png')
    logo = Image.open(logo_path)
    logo_width, logo_height = logo.size
    logo_scaling = (bar_height-5)/logo_height
    pdf.setFillColorRGB(0,0,0)
    pdf.rect(0, height-bar_height, width, bar_height, fill=True, stroke=False)
    pdf.drawImage(logo_path, 5, height-logo_height*logo_scaling, logo_width*logo_scaling, logo_height*logo_scaling)

    pdf.setFont('VeraBd', 9)
    pdf.setFillColorRGB(1,1,1) 
    pdf.drawString(width-165, height-bar_height+25, "User ID")
    pdf.drawString(width-120, height-bar_height+25, f": {history.user.id}")
    pdf.drawString(width-165, height-bar_height+15, "Cal. ID")
    pdf.drawString(width-120, height-bar_height+15, f": {history.id}")
    pdf.drawString(width-165, height-bar_height+5, "Date")
    pdf.drawString(width-120, height-bar_height+5, f": {date_time}")

    starting_spacer = 25
    subtitle_spacer = 40
    line_spacer = 5
    row_spacer = 15

    # Subtitle - Product Information
    pdf.setFont('VeraBd', 18)
    pdf.setFillColorRGB(0,0,0) 
    current_height = height-bar_height-starting_spacer  
    pdf.drawString(padding, current_height, "Product Information")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding, current_height) 
    # Series Name
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Series")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model.series}")
    # Model Name
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Model")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model}")
    # Flow configuration
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Flow Configuration")
    # print(f"{hist.calculation.flow_orientaion}")
    pdf.drawString(width/2, current_height, f"{hist.calculation.flow_orientaion}")   
    # Refrigerant
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Refrigerant")
    pdf.drawString(width/2, current_height, f"{hist.calculation.comp.refrigerant}")
    # Unit Dimension
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Unit Dimension LxDxH")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model.length} x {hist.calculation.model.depth} x {hist.calculation.model.height} mm3")
    # Power Supply
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Power Supply")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model.power_supply}")

    # Subtitle - Fan Information
    pdf.setFont('VeraBd', 18)
    current_height -= subtitle_spacer
    pdf.drawString(padding, current_height, "Fan Information")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding*2, current_height) 
    # Fan Type
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Fan Type")
    pdf.drawString(width/2, current_height, f"{MotorType.objects.get(pk=hist.calculation.model.fan.type).type} {hist.calculation.model.fan.size} D")
    # No. of Fan
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "No. of Fan")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.model.number_of_fan}")
    # Fan Speed
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Fan Speed")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.fan_rpm} RPM")
    # Filter Type
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Filter Type")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.filter.upper()}")
    # Airflow Rate
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Airflow Rate")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.airflow} m3/hr")
    # ESP
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "External Static Pressure")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.esp} Pa")
    # TSP
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Total Static Pressure")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.tsp} Pa")
    # Motor Heat
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Motor Heat")
    pdf.drawString(width/2, current_height,  f"{hist.calculation.fan_power} kW")

    # Subtitle - Entering Air Properties
    pdf.setFont('VeraBd', 18)
    current_height -= subtitle_spacer
    pdf.drawString(padding, current_height, "Entering Air Properties")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding*2, current_height) 
    # Dry Bulb Temperature
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Dry Bulb Temperature")
    pdf.drawString(width/2, current_height, f"{hist.calculation.inlet_temp} °C")
    # RH
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Relative Humidity")
    pdf.drawString(width/2, current_height, f"{hist.calculation.inlet_rh} %")

    # Subtitle - Entering Air Properties
    pdf.setFont('VeraBd', 18)
    current_height -= subtitle_spacer
    pdf.drawString(padding, current_height, "Outlet Air Properties")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding*2, current_height) 
    # Dry Bulb Temperature
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Dry Bulb Temperature")
    pdf.drawString(width/2, current_height, f"{hist.calculation.outlet_temp} °C")
    # RH
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Relative Humidity")
    pdf.drawString(width/2, current_height, f"{hist.calculation.outlet_rh} %")

    # Subtitle - Refrigeration System/Circuit
    pdf.setFont('VeraBd', 18)
    current_height -= subtitle_spacer
    pdf.drawString(padding, current_height, "Refrigeration System/Circuit")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding*2, current_height) 
    
    pdf.setFont('VeraBd', 11)
    # Ambient Temperature
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Ambient Temperature")
    pdf.drawString(width/2, current_height, f"{hist.calculation.amb_temp} °C")
    # No of Circuit
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "No. of Circuit")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model.number_of_compressor}")
    # Condenser Model
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Condenser Model")
    pdf.drawString(width/2, current_height, f"{hist.calculation.cond.get_model_name()}")
    # Heat Rejection
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Heat Rejection")
    pdf.drawString(width/2, current_height, f"{hist.calculation.heat_rejection} kW")
    # Compressor
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Compressor Size")
    pdf.drawString(width/2, current_height, f"{hist.calculation.model.compressor.hp}HP")
    # Evaporating Temperature
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Evaporating Temperature")
    pdf.drawString(width/2, current_height, f"{hist.calculation.t_evap} °C")
    # Condensing Temperature
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Condensing Temperature")
    pdf.drawString(width/2, current_height, f"{hist.calculation.t_cond} °C")
    # Compressor Power Input
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Compressor Power Input")
    pdf.drawString(width/2, current_height, f"{round(hist.calculation.heat_rejection - hist.calculation.total_cap/hist.calculation.model.number_of_compressor, 2)} kW")

    # Subtitle - Unit Capacity
    pdf.setFont('VeraBd', 18)
    current_height -= subtitle_spacer
    pdf.drawString(padding, current_height, "Unit Capacity")
    current_height -= line_spacer
    pdf.line(padding, current_height, width-padding*2, current_height) 
    # Gross Total Capacity
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Gross Total Capacity")
    pdf.drawString(width/2, current_height, f"{hist.calculation.total_cap} kW")
    # Gross Sensible Capacity
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Gross Sensible Capacity")
    pdf.drawString(width/2, current_height, f"{hist.calculation.sen_cap} kW")
    # Gross SHR
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Gross SHR")
    pdf.drawString(width/2, current_height, f"{round(hist.calculation.sen_cap/hist.calculation.total_cap, 2)}")
    # Net Total Capacity
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Net Total Capacity")
    pdf.drawString(width/2, current_height, f"{round(hist.calculation.total_cap - hist.calculation.fan_power, 2)} kW")
    # Gross Sensible Capacity
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Net Sensible Capacity")
    pdf.drawString(width/2, current_height, f"{round(hist.calculation.sen_cap- hist.calculation.fan_power, 2)} kW")
    # Gross SHR
    pdf.setFont('VeraBd', 11)
    current_height -= row_spacer
    pdf.drawString(padding*2, current_height, "Net SHR")
    pdf.drawString(width/2, current_height, f"{round((hist.calculation.sen_cap - hist.calculation.fan_power)/(hist.calculation.total_cap- hist.calculation.fan_power), 2)}")

    pdf.save()
    

