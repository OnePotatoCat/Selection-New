from Unit import Unit
from Coil import Coil
from Compressor import Compressor
from Condenser import Condenser
from Evaporator import Evaporator
from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir
import math

ATM_PRESSURE = 14.7
T_EVAP_MAX = 15.0
T_EVAP_MIN = 0.0
T_COND_MAX = 60
T_COND_MIN = 30
DENSITY = 1.176103


def main(t, rh, q):
    # Declare component
    comp = Compressor("zr72kce")
    evap = Evaporator("es20")
    cond = Condenser("hec274")
    unit = Unit("esu20aes", 50, "g4")
    # MAX_AIRFLOW =unit.evaporator.max_airflow
    # MIN_AIRFLOW = unit.evaporator.min_airflow

    # Inlet air Properties
    t_inlet = t
    rh_inlet = rh

    # Outdoor ambient temperature/Condenser airflow/massflow rate 
    t_amb = 35
    cond_airflow =7885
    cond_massflow = DENSITY*cond_airflow/3600
    
    # Airflow/Massflow rate
    airflow = q
    massflow = DENSITY*airflow/3600

    # Calculating Total Static Pressure and Fan Motor performance
    total_static_pressure = unit.get_tsp(airflow)
    unit.fan.set_properties(airflow, total_static_pressure)
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
    h_inlet = inlet_air.enthalpy/1000
    w_inlet = inlet_air.humidity

    # Design suction superheat and subcool 
    sh_suction = 6
    subcool = 5

    # Initiate Calculation
    t_evap_temp_max = T_EVAP_MAX
    t_evap_temp_min = T_EVAP_MIN
    t_cond_temp_max = T_COND_MAX
    t_cond_temp_min = T_COND_MIN
    flag_dew = False
    flag_condenser = False
    flag_compressor = False

    while(not flag_condenser):
        t_cond = 0.5*(t_cond_temp_max + t_cond_temp_min)
        flag_compressor = False

        while(not flag_compressor):
            t_evap = 0.5*(t_evap_temp_max + t_evap_temp_min)
            t1 = t_evap+sh_suction

            # ---------- Refrigerant Data ---------- # 
            # Point 1a - Evaporator Outlet
            refrigerant1a = Fluid(FluidsList.R407C).with_state(
                Input.temperature(t_evap),
                Input.quality(100)
            )
            h1a = (refrigerant1a.enthalpy)/1000
            pres_evaporating = ConvertPa_Psi(refrigerant1a.pressure) - ATM_PRESSURE

            # Point 1 - Evaporator Outlet
            refrigerant1 = Fluid(FluidsList.R407C).with_state(
                Input.temperature(t1),
                Input.pressure(ConvertPsi_Pa(pres_evaporating+ATM_PRESSURE))
            )
            h1 = (refrigerant1.enthalpy)/1000
            Q_sh = (h1 - h1a)*1061/3600 

            # Point 2a - Condenser Saturated Inlet
            refrigerant2a= Fluid(FluidsList.R407C).with_state(
                Input.temperature(t_cond),
                Input.quality(100)
            )
            pres_2a = ConvertPa_Psi(refrigerant2a.pressure) - ATM_PRESSURE

            # Point 2b - Condenser Mid Point
            refrigerant2b= Fluid(FluidsList.R407C).with_state(
                Input.quality(50.4),
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE))
            )
            t_cond_mid = refrigerant2b.temperature

            # Point 3a - Condenser Saturated Outlet
            refrigerant3a= Fluid(FluidsList.R407C).with_state(
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE)),
                Input.quality(0)
            )
            t3 = refrigerant3a.temperature - subcool

            # Point 3 - Condenser Saturated Outlet
            refrigerant3a= Fluid(FluidsList.R407C).with_state(
                Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE)),
                Input.temperature(t3)
            )
            h3 = refrigerant3a.enthalpy/1000

            # Point 4 - Evaporator Inlet
            refrigerant1= Fluid(FluidsList.R407C).with_state(
                Input.enthalpy(h3*1000),
                Input.pressure(ConvertPsi_Pa(pres_evaporating + ATM_PRESSURE))
            )
            h4 = (refrigerant1.enthalpy)/1000
            t4 = refrigerant1.temperature

            # Point 4b - Evaporating Mid Point
            refrigerant4b= Fluid(FluidsList.R407C).with_state(
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
            app_air = HumidAir().with_state(
                InputHumidAir.altitude(0),
                InputHumidAir.temperature(t_evap),
                InputHumidAir.relative_humidity(100)
            )
            h_app = app_air.enthalpy/1000
            w_app = app_air.humidity
            
            U_h_new = 30/1000
            
            unit.compressor.set_properties(t_evap, t_cond)
            cap_comp = unit.compressor.get_capacity()

            t_startdew = t_evap + starting_dewpoint(airflow/3600/unit.evaporator.frontal_area, t_evap,t_inlet)
            
            if (dp_inlet <= t_startdew) and (not flag_dew):
                Q_total = dry_capacity(unit.evaporator,t_inlet, t_evap, t_evap_mid, airflow)
                Q_sen = Q_total

                h_outlet = h_inlet - Q_sen/massflow
                outlet_air = HumidAir().with_state(
                    InputHumidAir.altitude(0),
                    InputHumidAir.enthalpy(h_outlet*1000),
                    InputHumidAir.humidity(w_inlet)
                )
                t_outlet = outlet_air.temperature
                try:
                    rh_outlet = outlet_air.relative_humidity
                except ValueError:
                    flag_dew = True
                    rh_outlet = 100


            else:
                flag_U = False
                while(not flag_U):
                    U_h_guess = U_h_new

                    h_outlet = h_saturated_te +(h_inlet-h_saturated_te)*math.exp(-U_h_guess*unit.evaporator.surface_area/massflow)
                    w_outlet = w_inlet - ((h_inlet - h_outlet)*(w_inlet - w_app))/(h_inlet - h_app) 

                    # Apparent Outlet Air Properties
                    app_outlet_air = HumidAir().with_state(
                        InputHumidAir.altitude(0),
                        InputHumidAir.enthalpy(h_outlet*1000),
                        InputHumidAir.humidity(w_outlet)
                    )
                    t_outlet = app_outlet_air.temperature 

                    # Apparent Outlet Air Properties
                    outlet_air = HumidAir().with_state(
                        InputHumidAir.altitude(0),
                        InputHumidAir.temperature(t_outlet),
                        InputHumidAir.humidity(w_outlet)
                    )
                    t_outlet = outlet_air.temperature
                    h_real_outlet = outlet_air.enthalpy/1000 
                    try:
                        rh_outlet = outlet_air.relative_humidity
                    except ValueError:
                        rh_outlet = 100
                    

                    # Sensible Air Point
                    sensible_air = HumidAir().with_state(
                        InputHumidAir.altitude(0),
                        InputHumidAir.humidity(w_outlet),
                        InputHumidAir.temperature(t_inlet)
                    )
                    h_sensible= sensible_air.enthalpy/1000

                    Q_sen = massflow * (h_sensible - h_real_outlet) 
                    lmed = (h_inlet - h_outlet)/math.log((h_inlet - h_saturated_te)/(h_outlet - h_saturated_te))
                    
                    U_h_new = unit.evaporator.U_wet(t_inlet, dp_inlet, t_evap, airflow/3600/unit.evaporator.frontal_area)/1000 
                    Q_total = U_h_new* unit.evaporator.surface_area * lmed 

                    if (U_h_new - U_h_guess)**2 < 10 ** (-9):
                        flag_U= True

            if ((cap_comp-0.05) - Q_total)**2 < 10 ** (-5):
                flag_compressor = True
            elif ((cap_comp-0.05) - Q_total) > 0:
                t_evap_temp_max = t_evap
            else:
                t_evap_temp_min= t_evap

        heat_reject = unit.compressor.get_power() + cap_comp
        condenser_cap = dry_capacity(unit.condenser, t_amb, t_cond, t_cond_mid, cond_airflow)
        if (condenser_cap - (heat_reject+0.05))**2 < 10**(-5):
            flag_condenser = True
        elif (condenser_cap - (heat_reject+0.05)) > 0:
            t_evap_temp_max = t_evap_temp_max +1
            t_evap_temp_min = t_evap_temp_min -1
            t_cond_temp_max = t_cond 
        else:
            t_evap_temp_max = t_evap_temp_max +1
            t_evap_temp_min = t_evap_temp_min -1
            t_cond_temp_min= t_cond 

    
    print(f"Compressor Capacity = {round(cap_comp, 2)}")
    print(f"Coil Total Capacity = {round(Q_total, 2)}")
    print(f"Coil Sensible Capacity = {round(Q_sen, 2)}")
    print(f"Superheat Capacity = {round(Q_sh, 2)}")
    print(f"Outlet Temp = {round(t_outlet, 2)}")
    print(f"Outlet RH = {round(rh_outlet, 2)}")
    print(f"Fan Power = {round(fan_power,2)}")
    print(f"Fan RPM = {round(fan_rpm,0)}")
    print(f"Evaporating Temp = {round(t_evap, 2)}")
    print(f"Condensing Temp = {round(t_cond, 2)}")
    print(f"Heat Reject = {round(heat_reject, 2)}")
    print(f"Condenser Capacity = {round(condenser_cap, 2)}")
    return Q_total


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
    main()
