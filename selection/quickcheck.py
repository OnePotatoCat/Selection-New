from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir

def ConvertPsi_Pa(pressure_psi):
    return pressure_psi*6894.75728


def ConvertPa_Psi(pressure_pa):
    return pressure_pa/6894.75728

ATM_PRESSURE = 14.7

water_in = Fluid(FluidsList.Water).with_state(
            Input.temperature(28),
            Input.pressure(101325),
        )

water_out = Fluid(FluidsList.Water).with_state(
            Input.temperature(33),
            Input.pressure(101325),
        )

dH = water_out.enthalpy-water_in.enthalpy
mdot= 12.5/3600
rho = (water_in.density+water_out.density)/2
q=mdot*rho*dH
Q_need = 51.6*1000*2

mdot_need = Q_need/dH
vdot_need = mdot_need/rho*3600
# refrigerant = FluidsList.R513A
# ref_point= Fluid(refrigerant).with_state(
#     Input.temperature(20),
#     Input.quality(100)
# )

# pres_evaporating = ConvertPa_Psi(ref_point.pressure) - ATM_PRESSURE

# ref_out = Fluid(refrigerant).with_state(
#     Input.temperature(26),
#     Input.pressure(pres_evaporating)
# ) 




print(mdot_need)

