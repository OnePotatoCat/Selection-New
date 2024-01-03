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
         t :float, rh :float, q :float, t_win :float, t_wout :float,
         esp = 50.0, filter_type="g4"):
    
    # Declare component
    unit = Unit_Cal.as_cw(unit_id,cw_id, fan_id, esp, filter_type)

    # Inlet air Properties
    t_inlet = t
    rh_inlet = rh
    
    # Airflow/Massflow rate
    airflow = q
    massflow = DENSITY*airflow/3600
    v=airflow/3600/unit.cw.frontal_area

    # Calculating Total Static Pressure and Fan Motor performance
    total_static_pressure = unit.get_tsp(airflow)

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

    print(f'{v}  {t_inlet} {t_win} {t_wout}')
    t_stardew= unit.cw.starting_dewpoint(v, t_inlet, t_win, t_wout)

    if(dp_inlet <= t_stardew):
        # Dry Coil Evaporator Capacity Calculation
        m_dot = unit.cw.mdot_dry(v, t_inlet, t_win, t_wout)
        Q_total = (m_dot/3600)*4.18*(t_wout-t_win)
        Q_sen = Q_total
        h_outlet = h_inlet - Q_sen/massflow
        outlet_air = HumidAir().with_state(
            InputHumidAir.altitude(0),
            InputHumidAir.enthalpy(h_outlet*1000),
            InputHumidAir.humidity(w_inlet)
        )
        t_outlet = outlet_air.temperature
        rh_outlet = outlet_air.relative_humidity

        dp = unit.cw.pressure_drop(m_dot)

        print(f'Total Capacity: {Q_total:.2f} ')
        print(f'Outlet Temp: {t_outlet:.2f} ')
        print(f'Outlet RH: {rh_outlet:.2f} ')
        print(f'Flow Rate:{m_dot:.2f} ')
        print(f'Pressure Drop:{dp:.2f} ')

    else:
        # massflow rate of water
        m_dot = unit.cw.mdot_wet(v, t_inlet, dp_inlet, t_win, t_wout)
        
        # Total capacity of water
        Q_total = (m_dot/3600)*4.18*(t_wout-t_win)
        print(Q_total)
        h_outlet = h_inlet - Q_total/massflow
        U_wet = unit.cw.U_wet(v, t_inlet, dp_inlet, t_win, t_wout)
        bypass = math.exp(-U_wet*unit.cw.surface_area/(m_dot))

        # apperant air properties 
        t_app = 0.5*(t_win + t_wout)
        app_air = HumidAir().with_state(
                InputHumidAir.altitude(0),
                InputHumidAir.temperature(t_app),
                InputHumidAir.relative_humidity(100)
            )
        w_app = app_air.humidity

        # Outlet air properties
        w_outlet = w_app + (w_inlet - w_app) * bypass
        print(m_dot)
        print(w_outlet)
        print(h_outlet)
        outlet_air = HumidAir().with_state(
            InputHumidAir.altitude(0),
            InputHumidAir.enthalpy(h_outlet*1000),
            InputHumidAir.humidity(w_outlet)
        )
        t_outlet = outlet_air.temperature
        rh_outlet = outlet_air.relative_humidity


        # Sensible air point
        sensible_air = HumidAir().with_state(
            InputHumidAir.altitude(0),
            InputHumidAir.humidity(w_outlet),
            InputHumidAir.temperature(t_inlet)
        )
        h_sensible = sensible_air.enthalpy/1000

        Q_lat = massflow*(h_inlet - h_sensible)
        Q_sen = Q_total - Q_lat
        dp = unit.cw.pressure_drop(m_dot)




        print(f'Total Capacity: {Q_total:.2f} ')
        print(f'Sensible Capacity: {Q_sen:.2f} ')
        print(f'Outlet Temp.: {t_outlet:.2f} ')
        print(f'Outlet RH: {rh_outlet:.2f} ')
        print(f'Flow Rate:{m_dot:.2f} ')
        print(f'Pressure Drop:{dp:.2f}')

        
    """
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


    unit.total_capacity = Q_total
    unit.sensible_capacity = Q_sen
    unit.outlet_temp = t_outlet_net
    unit.outlet_rh = rh_outlet_net

    
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
    """
    return 


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


def ConvertPsi_Pa(pressure_psi):
    return pressure_psi*6894.75728

def ConvertPa_Psi(pressure_pa):
    return pressure_pa/6894.75728

if __name__ == "__main__":
    main(24, 46.1, 5550)