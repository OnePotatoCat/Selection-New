from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir
import math
import sys
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

sys.path.append('../../selection')
from .Unit import Unit_Cal
from .Coil import Coil
from .Compressor import Compressor_Cal
from .Condenser import Condenser_Cal
from .Evaporator import Evaporator_Cal
from .CWCoil import CWCoil_Cal

ATM_PRESSURE = 14.7
DENSITY = 1.176103
MAX_COUNTER = 1000

def main(unit_id :int, cw_id :int, fan_id :int, 
         t :float, rh :float, q :float, 
         esp = 50.0, filter_type="g4"):
    
    # Declare component
    unit = Unit_Cal.as_cw(unit_id, cw_id, fan_id, esp, filter_type)

    # Inlet air Properties
    t_inlet = t
    rh_inlet = rh
    
    # Airflow/Massflow rate
    airflow = q
    massflow = DENSITY*airflow/3600

    # Calculating Total Static Pressure and Fan Motor performance
    total_static_pressure = unit.get_tsp(airflow)
    print(unit.fan.type)
    # checking for AC fan= 1
    if unit.fan.type == 1:
        unit.fan.get_ac_staticpressure(airflow)
        fan_power = unit.fan.get_power()
        fan_rpm = unit.fan.get_rpm()
        fan_current = unit.fan.get_current()
    else:
        unit.fan.set_properties(airflow/unit.no_of_fan, total_static_pressure)
        fan_power = unit.fan.get_power()
        fan_rpm = unit.fan.get_rpm()
        fan_current = unit.fan.get_current()

    # Calculate inlet air properties
    inlet_air = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.temperature(t_inlet),
        InputHumidAir.relative_humidity(rh_inlet)
    )
    dp_inlet = inlet_air.dew_temperature
    wb_inlet = inlet_air.wet_bulb_temperature
    h_inlet = inlet_air.enthalpy/1000
    w_inlet = inlet_air.humidity
    cp_inlet = inlet_air.specific_heat/1000


    # Initiate Calculation
    flag_dew = False
    flag_rh = True
    counter = 0

    


    t_outlet_net = t_outlet + unit.fan.get_power()/(massflow*1.006)
    net_outlet_air = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.humidity(w_outlet),
        InputHumidAir.temperature(t_outlet_net)
    )
    try:
        rh_outlet_net = net_outlet_air.relative_humidity
        wb_outlet_net = net_outlet_air.wet_bulb_temperature
    except:
        rh_outlet_net = 100
        wb_outlet_net = net_outlet_air.wet_bulb_temperature
        flag_rh = False

    # print("Issue")
    # print(w_outlet)
    # print(wb_outlet_net)
    # print(t_outlet_net)

    # print(f'{t_inlet} , {dp_inlet}, {t_evap}, {airflow/3600/unit.evaporator.frontal_area}')
    # print(f'Uh :{U_h_new}')
    # print(f'Bypass : {bypass}')
    # print(f'LMED :{lmed}')
    # print(f't_evap_mid : {t_evap_mid}')
    # print(f'Hinlet :{h_inlet}')
    # print(f'Houtlet :{h_real_outlet}')
    # print(f'massflow :{massflow}')
    # print(f'{counter}')
    # print(f'{cond_airflow}, {condenser_cap}')
    # print(f'unit = {Q_total} | compressor = {cap_comp*number_comp}')
    # print(f'diff = {cap_comp*number_comp - Q_total}')
    # print(f'condenser = {condenser_cap} | heat_reject = {heat_reject}')
    # print(f'te = {t_evap} | tc = {t_cond}')
    # print(f'te_max = {t_evap_temp_max} | te_min = {t_evap_temp_min}')
    # print(f'tc_max = {t_cond_temp_max} | tc_min = {t_cond_temp_min}')

    unit.total_capacity = Q_total
    unit.sensible_capacity = Q_sen
    unit.outlet_temp = t_outlet_net
    unit.outlet_rh = rh_outlet_net
    unit.evaporator.saturated_temp = t_evap
    unit.condenser.saturated_temp = t_cond
    unit.compressor.get_power()

    cap_dict = {
        "Total Capacity": (round(Q_total, 2), "kW"),
        "Total Sensible Cap.": (round(Q_sen, 2), "kW"),
        "Net Capacity": (round(Q_total - fan_power*unit.no_of_fan, 2), "kW"),
        "Net Sensible Cap.": (round(Q_sen - fan_power*unit.no_of_fan, 2), "kW")
    }

    fan_dict = {
        # "Fan": (unit.fan.model.upper(), ""),
        "Fan": (unit.fan.size, ""),
        "Airflow": (round(airflow, 2), "m3/hr"),
        "Fan Power": (round(fan_power, 2), "kW"),
        "Fan RPM": (round(fan_rpm,0), "rpm"),
        "Total Static Pressure": (round(unit.tsp, 0), "Pa")
    }

    comp_dict = {
        # "Compressor": (unit.compressor.model.upper(), ""),
        "Compressor": (str(unit.compressor.hp) + "HP", ""),
        "Comp. Power": (round(unit.compressor.get_power(), 1), "kW"),
        # "Comp. Current": (round(unit.compressor.get_current(), 1), "A"),
        "Evaporating Temp.": (round(t_evap, 1), "°C"),
        "Condensing Temp.": (round(t_cond, 1), "°C")
    }

    air_dict = {
        "Off Coil Temperature": (round(t_outlet, 1), "°C"),
        "Off Coil RH": (round(rh_outlet, 1), "%"),
        "Outlet Temperature": (round(t_outlet_net, 1), "°C"),
        "Outlet RH": (round(rh_outlet_net, 1), "%")
    }

    performance_dict = {
        "converged": check_diverge_counter(counter) and flag_rh,
        "high_tc": t_cond>T_COND_LIMIT,
        "capacity": cap_dict,
        "fan": fan_dict,
        "compressor": comp_dict,
        "air": air_dict
    }

    return performance_dict


def check_diverge_counter(counter: int) -> bool:
    if counter < MAX_COUNTER:
        return True 
    return False


def dry_capacity(coil :Coil,t_drybulb :float, t_sat :float, t_sat_mid :float, airflow :float):
    delta_t = abs(t_drybulb - t_sat)
    velocity = airflow/3600/coil.frontal_area
    U = coil.U_dry(abs(t_drybulb - t_sat), velocity)

    UA = U*coil.surface_area
    massflow = DENSITY*airflow/3600
    cp_min = massflow * 1.006
    NTU = UA /1000/cp_min
    e = 1 - math.exp(-NTU)

    return abs(e*cp_min*(t_drybulb - t_sat_mid))


def starting_dewpoint(vel :float, t_evap :float, t_inlet :float):
    c = [-1.170695802,
        0.28936308,
        0.008312431,
        -0.059279856,
        -0.00982999,
        0.043792714,
        0.000587257
        ]   

    t_startdew = t_evap+ c[0] + c[1] * vel + c[2] * t_evap + c[3] * vel * t_evap + \
                 c[4] * t_inlet + c[5] * t_inlet * vel + c[6] * t_inlet * t_evap

    return t_startdew


def LMED_U(t_drybulb :float, t_dewpoint :float, t_evap :float, vel :float):
    c = [12.29230419,
         0.398495745,
         0.123584793,
         -0.650576675,
         6.853474482,
         -0.124564167,
         0.011297419,
         -0.009147343,
         -0.003567652
        ]

    LMDED_U = c[0] + c[1] * t_dewpoint + c[2] * t_drybulb + c[3] * t_evap + c[4] * vel + \
              c[5] * t_evap * vel + c[6] * vel / (t_drybulb - t_dewpoint) + \
              c[7] * (t_dewpoint - t_evap) ** 2 + c[8] * vel * (t_dewpoint - t_evap) ** 2

    return LMDED_U


def ConvertPsi_Pa(pressure_psi):
    return pressure_psi*6894.75728


def ConvertPa_Psi(pressure_pa):
    return pressure_pa/6894.75728

if __name__ == "__main__":
    main(24, 46.1, 5550)