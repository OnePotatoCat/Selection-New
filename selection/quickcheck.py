from pyfluids import Fluid, FluidsList, Input, HumidAir, InputHumidAir


water = Fluid(FluidsList.Water).with_state(
            Input.temperature(30),
            Input.pressure(101325),
        )

print(water.density)