from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir
import math
import sys
from Compressor import Compressor

ATM_PRESSURE = 14.7

def main():
    Te_dew = 9
    Tc_dew = 50

    sh_suction = 6
    subcool = 5

    t1 = Te_dew+sh_suction

    # Point 1a - Evaporator Outlet
    refrigerant1a = Fluid(FluidsList.R407C).with_state(
        Input.temperature(Te_dew),
        Input.quality(100)
    )
    h1a = (refrigerant1a.enthalpy)/1000
    pres_evaporating = ConvertPa_Psi(refrigerant1a.pressure) - ATM_PRESSURE
    print(f"Evaporating Pressure = {round(pres_evaporating, 2)}")    


    refrigerant1 = Fluid(FluidsList.R407C).with_state(
        Input.temperature(t1),
        Input.pressure(ConvertPsi_Pa(pres_evaporating+ATM_PRESSURE))
    )
    h1 = (refrigerant1.enthalpy)/1000
    Q_sh = (h1 - h1a)*1061/3600  
    print(f"Superheater Capacity = {Q_sh}")

    # Point 2a - Condenser Inlet
    refrigerant1= Fluid(FluidsList.R407C).with_state(
        Input.temperature(Tc_dew),
        Input.quality(100)
    )
    pres_2a = ConvertPa_Psi(refrigerant1.pressure) - ATM_PRESSURE
    print(f"Point 2a Condensing Pressure = {round(pres_2a, 2)}")

    # Point 3a - Condenser Saturated Outlet
    refrigerant3a= Fluid(FluidsList.R407C).with_state(
        Input.pressure(ConvertPsi_Pa(pres_2a + ATM_PRESSURE)),
        Input.quality(0)
        # Input.temperature(Tc_dew - subcool)
    )
    t3 = refrigerant3a.temperature-subcool

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
    print(f"Point 1 Enthalpy= {round(h1,2)}")
    print(f"Point 4 Enthalpy= {round(h4,2)}")


    # Point 4a - Evaporating Mid Point
    refrigerant1= Fluid(FluidsList.R407C).with_state(
        Input.quality(62),
        Input.pressure(ConvertPsi_Pa(pres_evaporating + ATM_PRESSURE))
    )
    te_mid = refrigerant1.temperature
    print(f"Mid point Evap Temp = {round(te_mid, 2)} C")


    # Inlet Air Prop
    humidair_inlet = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.temperature(30),
        InputHumidAir.relative_humidity(40)
    )
    h_air_inlet = humidair_inlet.enthalpy/1000
    w_air_inlet = humidair_inlet.humidity
    print(f"Inlet air enthalpy = {round(h_air_inlet, 2)}")


    # Air Prop Saturated @ Te 
    humidair_Te = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.temperature(te_mid),
        InputHumidAir.relative_humidity(100)
    )
    h_air_saturated_te = humidair_Te.enthalpy/1000
    print(f"Te Saturated air enthalpy = {round(h_air_saturated_te, 2)}")


    U = 29/1000
    A = 64.76
    ma = 8029/3600

    # Theerakulpisut Method
    print("+============================Theerakulpisut Method=============================+")
    print(f"UA/M = {math.exp(-U*A/ma)}")
    h_air_outlet = h_air_saturated_te +(h_air_inlet-h_air_saturated_te)*math.exp(-U*A/ma)

    print(f"Estimated air outlet enthalpy = {round(h_air_outlet, 2)}")

    lmed = (h_air_inlet - h_air_outlet)/math.log((h_air_inlet - h_air_saturated_te)/(h_air_outlet - h_air_saturated_te))
    print(f"LMED = {round(lmed, 2)}")

    Qtotal = U*A*lmed
    print(f"Total Capacity ={round(Qtotal,2)} kW")


    # Apparatus Dewpoint Air Prop
    humidair_app = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.relative_humidity(100),
        InputHumidAir.temperature(Te_dew)
    )
    h_air_app = humidair_app.enthalpy/1000
    print(f"Apparatus Dewpoint Air Enthalpy = {round(h_air_app,2)}")
    w_air_app = humidair_app.humidity
    print(f"Apparatus Air Humidity = {round(w_air_app*1000,2)}")


    # Outlet Air Prop
    w_air_outlet = w_air_inlet - ((h_air_inlet - h_air_outlet)*(w_air_inlet - w_air_app))/(h_air_inlet - h_air_app) 
    humidair_outlet = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.enthalpy(h_air_outlet*1000),
        InputHumidAir.humidity(w_air_outlet)
    )

    t_air_out = humidair_outlet.temperature - Q_sh/(ma*1.006)
    # Actual Outlet Air Prop
    humidair_outlet_act = HumidAir().with_state(
        InputHumidAir.altitude(0),
        InputHumidAir.temperature(t_air_out),
        InputHumidAir.humidity(w_air_outlet)
    )

    print(f"Outlet Air Temperature = {round((humidair_outlet_act.temperature), 2)} C")
    print(f"Outlet Air RH = {round((humidair_outlet_act.relative_humidity), 2)} %")
    print("+=========================End of Theerakulpisut Method==========================+")
    print("\n")

    # Compressor 
    compressor_model = "zr72kce"
    compressor = Compressor(compressor_model)
    print(compressor.capacity(Te_dew,50))


def EstimateAirExitEnthalpy():
    return None

def ConvertPsi_Pa(pressure_psi):
    return pressure_psi*6894.75728

def ConvertPa_Psi(pressure_pa):
    return pressure_pa/6894.75728


if __name__ == "__main__":
    main()
