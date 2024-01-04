from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir
import math
import sys
from sklearn.linear_model import LinearRegression
import pickle
from .models import ChillwaterCoil as cw

sys.path.append('../../selection')
from .Unit import Unit_Cal
from .Coil import Coil
from .Compressor import Compressor_Cal
from .Condenser import Condenser_Cal
from .Evaporator import Evaporator_Cal

ATM_PRESSURE = 14.7
T_EVAP_MAX = 15
T_EVAP_MIN = 1
T_COND_MAX = 60
T_COND_MIN = 30
T_COND_LIMIT =52.1
DENSITY = 1.176103
MAX_COUNTER = 1000

def main(unit_id :int, evap_id :int, cond_id :int, comp_id :int, fan_id :int, 
        t :float, rh :float, q :float, 
        esp = 50.0, abm_temp = 35, comp_speed = 100.0, filter_type="g4"):
    
    # Declare component
    unit = Unit_Cal.as_dx(unit_id, evap_id, cond_id, comp_id, fan_id, esp, filter_type)

    # Determine refrigerant type
    if unit.compressor.refrigerant == "R407C":
        refrigerant = FluidsList.R407C
    elif unit.compressor.refrigerant == "R410A":
        refrigerant = FluidsList.R410A

    # Determine inverter model 
    if unit.compressor.inverter:
        freq = comp_speed

    # Inlet air Properties
    t_inlet = t
    rh_inlet = rh

    # Outdoor ambient temperature/Condenser airflow/massflow rate 
    t_amb = abm_temp
    cond_airflow = unit.condenser.airflow
    # cond_massflow = DENSITY*cond_airflow/3600
    
    # Airflow/Massflow rate
    airflow = q
    massflow = DENSITY*airflow/3600

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

    # Design suction superheat and subcool
    sh_suction = 6
    subcool = 5

    # Initiate Calculation
    t_evap_temp_max = unit.compressor.evap_temp_limit
    T_EVAP_MAX = unit.compressor.evap_temp_limit
    t_evap_temp_min = T_EVAP_MIN
    t_cond_temp_max = T_COND_MAX
    t_cond_temp_min = T_COND_MIN
    flag_dew = False
    flag_condenser = False
    flag_compressor = False
    flag_rh = True
    counter = 0
    prev_Uh = 0
    lmed = 0

    while(not flag_condenser) and (check_diverge_counter(counter)):
        t_cond = 0.5*(t_cond_temp_max + t_cond_temp_min)
        flag_compressor = False

        while(not flag_compressor) and (check_diverge_counter(counter)):
            t_evap = 0.5*(t_evap_temp_max + t_evap_temp_min)
            t1 = t_evap+sh_suction

            # ---------- Refrigerant Data ---------- # 
            # Point 1a - Evaporator Outlet
            refrigerant1a = Fluid(refrigerant).with_state(
                Input.temperature(t_evap),
                Input.quality(100)
            )
            h1a = (refrigerant1a.enthalpy)/1000
            pres_evaporating = ConvertPa_Psi(refrigerant1a.pressure) - ATM_PRESSURE

            # Point 1 - Evaporator Outlet
            refrigerant1 = Fluid(refrigerant).with_state(
                Input.temperature(t1),
                Input.pressure(ConvertPsi_Pa(pres_evaporating+ATM_PRESSURE))
            )
            h1 = (refrigerant1.enthalpy)/1000

            # Point 2a - Condenser Saturated Inlet
            refrigerant2a= Fluid(refrigerant).with_state(
                Input.temperature(t_cond),
                Input.quality(100)
            )
            pres_2a = ConvertPa_Psi(refrigerant2a.pressure) - ATM_PRESSURE

            # Point 2b - Condenser Mid Point
            refrigerant2b= Fluid(refrigerant).with_state(
                Input.quality(50.4),
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE))
            )
            t_cond_mid = refrigerant2b.temperature

            # Point 3a - Condenser Saturated Outlet
            refrigerant3a= Fluid(refrigerant).with_state(
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE)),
                Input.quality(0)
            )
            
            # Point 3 - Condenser Outlet
            t3 = refrigerant3a.temperature - subcool
            refrigerant3a= Fluid(refrigerant).with_state(
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE)),
                Input.temperature(t3)
            )
            h3 = refrigerant3a.enthalpy/1000

            # Point 4 - Evaporator Inlet
            refrigerant1= Fluid(refrigerant).with_state(
                Input.enthalpy(h3*1000),
                Input.pressure(ConvertPsi_Pa(pres_evaporating + ATM_PRESSURE))
            )
            h4 = (refrigerant1.enthalpy)/1000
            t4 = refrigerant1.temperature

            # Point 4b - Evaporating Mid Point
            refrigerant4b= Fluid(refrigerant).with_state(
                Input.quality(62),
                Input.pressure(ConvertPsi_Pa(pres_evaporating + ATM_PRESSURE))
            )
            t_evap_mid = refrigerant4b.temperature

            # ------ End Refrigerant Data -------- #


            # ---------- Air Side Data ---------- #
            # Air Prop Saturated @ Te 
            saturated_air = HumidAir().with_state(
                InputHumidAir.altitude(0),
                InputHumidAir.temperature(t_evap_mid),
                InputHumidAir.relative_humidity(100)
            )
            h_saturated_te = saturated_air.enthalpy/1000

            # Apparatus Air Properties
            if refrigerant == FluidsList.R407C:
                t_app = t_evap
            elif refrigerant == FluidsList.R410A:
                t_app = t_evap + 2.2
            else:
                t_app = t_evap
            
            app_air = HumidAir().with_state(
                InputHumidAir.altitude(0),
                InputHumidAir.temperature(t_app),
                InputHumidAir.relative_humidity(100)
            )
            w_app = app_air.humidity

            if prev_Uh != 0:
                U_h_new = prev_Uh
            else:   
                U_h_new = 30/1000

            if unit.compressor.inverter:
                unit.compressor.set_properties(t_evap, t_cond, freq)
            else:
                unit.compressor.set_properties(t_evap, t_cond)

            cap_comp = unit.compressor.get_capacity()
            number_comp = unit.no_of_comp

            t_startdew = unit.evaporator.starting_dewpoint(airflow/3600/unit.evaporator.frontal_area, t_evap,t_inlet)

            if (dp_inlet <= t_startdew) and (not flag_dew) and (check_diverge_counter(counter)):
                # Dry Coil Evaporator Capacity Calculation
                Q_total = dry_capacity(unit.evaporator,t_inlet, t_evap, t_evap_mid, airflow)
                Q_sen = Q_total
                h_outlet = h_inlet - Q_sen/massflow
                outlet_air = HumidAir().with_state(
                    InputHumidAir.altitude(0),
                    InputHumidAir.enthalpy(h_outlet*1000),
                    InputHumidAir.humidity(w_inlet)
                )
                t_outlet = outlet_air.temperature
                w_outlet = w_inlet

                counter += 1
                try:
                    rh_outlet = outlet_air.relative_humidity
                except ValueError:
                    flag_dew = True
                    rh_outlet = 100

            else:
                # Wet Coil Evaporator Capacity Calculation
                flag_U = False
                while(not flag_U and check_diverge_counter(counter)):
                    U_h_guess= U_h_new
                    
                    bypass = math.exp(-U_h_guess*unit.evaporator.surface_area/(massflow))
                    h_outlet = h_saturated_te +(h_inlet-h_saturated_te) * bypass
                    w_outlet = w_app + (w_inlet - w_app) * bypass
                    
                    # Apparent Outlet Air Properties
                    outlet_air = HumidAir().with_state(
                        InputHumidAir.altitude(0),
                        InputHumidAir.enthalpy(h_outlet*1000),
                        InputHumidAir.humidity(w_outlet)
                    )
                    t_outlet = outlet_air.temperature
                    h_real_outlet = outlet_air.enthalpy/1000 
                    try:
                        rh_outlet = outlet_air.relative_humidity
                    except ValueError:
                        flag_rh = False
                        rh_outlet = 100
                    

                    # Sensible Air Point
                    sensible_air = HumidAir().with_state(
                        InputHumidAir.altitude(0),
                        InputHumidAir.humidity(w_outlet),
                        InputHumidAir.temperature(t_inlet)
                    )
                    h_sensible= sensible_air.enthalpy/1000

                    lmed = (h_inlet - h_outlet)/math.log((h_inlet - h_saturated_te)/(h_outlet - h_saturated_te))
                    U_h_new = 1.05*unit.evaporator.U_wet(t_inlet, dp_inlet, t_evap, airflow/3600/unit.evaporator.frontal_area)/1000 
                    prev_Uh = U_h_new
                    Q_total = U_h_new* unit.evaporator.surface_area * lmed 
                    Q_lat = massflow * (h_inlet - h_sensible)
                    Q_sen = Q_total - Q_lat

                    counter += 1
                    if (U_h_new - U_h_guess)**2 < 10 ** (-5):
                        flag_U= True
            
            # print(f'U_h_new = {U_h_new*1000:.2f}')
            # if lmed:
            #     print(f'lmed = {lmed:.2f}')
            # print(f'unit = {Q_total:.2f} | compressor = {cap_comp*number_comp:.2f}')
            # print(f'te = {t_evap:.2f} | tc = {t_cond:.2f}')
            # print(f'te_max = {t_evap_temp_max:.2f} | te_min = {t_evap_temp_min:.2f}')
            # print(f'tc_max = {t_cond_temp_max:.2f} | tc_min = {t_cond_temp_min:.2f}')
            # print('-----------------------------------')

            if ((cap_comp*number_comp-(0.05)*number_comp) - Q_total)**2 < 10 ** (-5):
                flag_compressor = True
            elif ((cap_comp*number_comp-(0.05)*number_comp) - Q_total) > 0:
                t_evap_temp_max = t_evap + (t_evap_temp_max - t_evap)/2
            else:
                t_evap_temp_min= t_evap + (t_evap_temp_min - t_evap)/2

            if (t_evap_temp_max - t_evap_temp_min)**2 <  10 ** (-7):
                break
            

        # Condenser Capacity Calculation
        heat_reject = (unit.compressor.get_power() + cap_comp)*number_comp
        condenser_cap = dry_capacity(unit.condenser, t_amb, t_cond, t_cond_mid, cond_airflow)*number_comp
        
        if ((condenser_cap - (heat_reject+0.05))**2 < 10**(-5) and flag_compressor):
            flag_condenser = True
        elif (condenser_cap - (heat_reject+0.05)) > 0:
            t_evap_temp_max = t_evap_temp_max +2
            t_evap_temp_min = t_evap_temp_min -2
            t_cond_temp_max = t_cond + 2
        else:
            t_evap_temp_max = t_evap_temp_max +2
            t_evap_temp_min = t_evap_temp_min -2
            t_cond_temp_min = t_cond - 2

        if t_evap_temp_max > T_EVAP_MAX: t_evap_temp_max = T_EVAP_MAX
        if t_evap_temp_min < T_EVAP_MIN: t_evap_temp_min = T_EVAP_MIN


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