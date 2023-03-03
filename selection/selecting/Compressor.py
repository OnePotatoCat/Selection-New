from .models import Compressor as comp
from multipledispatch import dispatch

class Compressor_Cal(object):
    def __init__(self, comp_id :int) -> None:
        compressor = comp.objects.get(pk = comp_id)
        self.model = compressor.model
        self.refrigerant = compressor.refrigerant
        self.evap_temp_limit = compressor.evap_temp_limit
        self.cap_coef = compressor.capacity_coefficient
        self.pow_coef = compressor.power_coefficient
        self.cur_coef = compressor.current_coefficient
        self.mas_coef = compressor.current_coefficient
        self.inverter = compressor.inverter

        if not self.inverter:
            self.set_properties(10.0, 45.0)
        else:
            self.set_properties(10.0, 45.0, 100.0)


    def get_capacity(self) -> float:
        return self._capacity

    def get_power(self) -> float:
        return self._power

    def get_current(self) -> float:
        return self._current
    
    def get_massflow(self) -> float:
        return self._massflow


    # -----------------------------------------------------------
    # Set properties  
        # non-inverter model 
    @dispatch(float, float)
    def set_properties(self, t_evap :float, t_cond :float) -> float:
        self.set_capacity(t_evap, t_cond)
        self.set_power(t_evap, t_cond)
        self.set_current(t_evap, t_cond)
        self.set_massflow(t_evap, t_cond)

        # inverter model 
    @dispatch(float, float, float)
    def set_properties(self, t_evap :float, t_cond :float, freq :float) -> float:
        self.set_capacity(t_evap, t_cond, freq)
        self.set_power(t_evap, t_cond, freq)
        self.set_current(t_evap, t_cond, freq)
        self.set_massflow(t_evap, t_cond, freq)
    # -----------------------------------------------------------


    # -----------------------------------------------------------
    # Set Capacity  
    @dispatch(float, float)
    def set_capacity(self, t_evap, t_cond):
        # Output = Cooling Capacity (kW)
        self._capacity = self.calculate_properties(t_evap, t_cond, self.cap_coef)

    @dispatch(float, float, float)
    def set_capacity(self, t_evap, t_cond, freq):
        # Output = Cooling Capacity (kW)
        self._capacity = self.calculate_properties(t_evap, t_cond, freq, self.cap_coef)
    # -----------------------------------------------------------


    # -----------------------------------------------------------
    # Set Power  
    @dispatch(float, float)
    def set_power(self, t_evap, t_cond):
        # Output = Power Input (kW)
        self._power = self.calculate_properties(t_evap, t_cond, self.pow_coef)

    @dispatch(float, float, float)
    def set_power(self, t_evap, t_cond, freq):
        # Output = Power Input (kW)
        self._power = self.calculate_properties(t_evap, t_cond, freq, self.pow_coef)
    # -----------------------------------------------------------


    # -----------------------------------------------------------
    # Set Current  
    @dispatch(float, float)
    def set_current(self, t_evap, t_cond):
        # Output = Current (A)
        self._current = self.calculate_properties(t_evap, t_cond, self.cur_coef)
    
    @dispatch(float, float, float)
    def set_current(self, t_evap, t_cond, freq):
        # Output = Current (A)
        self._current = self.calculate_properties(t_evap, t_cond, freq, self.cur_coef)
    # -----------------------------------------------------------


    # -----------------------------------------------------------
    # Set Massflow  
    @dispatch(float, float)
    def set_massflow(self, t_evap, t_cond):
        # Output = Massflow Rate (kg/s)
        self._massflow = self.calculate_properties(t_evap, t_cond, self.mas_coef)  

    @dispatch(float, float, float)
    def set_massflow(self, t_evap, t_cond, freq):
        # Output = Massflow Rate (kg/s)
        self._massflow = self.calculate_properties(t_evap, t_cond, freq, self.mas_coef) 
    # -----------------------------------------------------------


    # -----------------------------------------------------------
    # Calculate Properties      
    @dispatch(float, float, list)
    def calculate_properties(self, t_evap, t_cond, c : list[float]) -> float:
        # t_evap = Evaporating Temperature (C)
        # t_cond = Condensing Temperature (C)
        # c = coefficient [0-9]
        output = c[0] + c[1] * t_evap + c[2] * t_cond + \
                c[3] * t_evap**2 + c[4] * t_evap * t_cond + c[5] * t_cond**2 + \
                c[6] * t_evap**3 + c[7] * t_evap**2 * t_cond + c[8] * t_evap * t_cond**2 + c[9] * t_cond**3
        return output

    @dispatch(float, float, float, list)
    def calculate_properties(self, t_evap, t_cond, freq, c : list[float]) -> float:
        # t_evap = Evaporating Temperature (C)
        # t_cond = Condensing Temperature (C)
        # freq = compressor speed (rps/hz)
        # c = coefficient [0-23]
        output = c[0] + c[1] * t_evap + c[2] * t_evap ** 2 + c[3] * t_evap ** 3 + \
                c[4] * t_cond + c[5] * t_cond * t_evap + c[6] * t_cond * t_evap ** 2 + c[7] * t_cond * t_evap ** 3 + \
                c[8] * t_cond ** 2 + c[9] * t_cond ** 2 * t_evap + c[10] * t_cond ** 2 * t_evap ** 2 + c[11] * t_evap ** 3 * t_cond ** 2 + \
                c[12] * freq + c[13] * freq * t_evap + c[14] * freq * t_evap ** 2 + c[15] * freq * t_evap ** 3 + \
                c[16] * freq ** 2 + c[17] * freq ** 2 * t_evap + c[18] * freq ** 2 * t_evap ** 2 + c[19] * freq ** 2 * t_evap ** 3 + \
                c[20] * freq ** 2 * t_cond + c[21] * freq ** 2 * t_cond * t_evap + c[22] * freq ** 2 * t_cond * t_evap ** 2 + c[23] * freq ** 2 * t_cond * t_evap ** 3
        return output
    # -----------------------------------------------------------

def main():
    compressor = Compressor_Cal(3)
    te = 10
    tc = 52
    compressor.set_properties(te, tc, 100)
    print(f"Compressor Model : {compressor.model}")
    print(f"Performance at Te={te} | Tc={tc}")
    print(f"Capacity = {round(compressor.get_capacity(),2)}")
    print(f"Power = {round(compressor.get_power(),2)}")
    print(f"Current = {round(compressor.get_current(),2)}")
    print(f"Massflow = {round(compressor.get_massflow(),2)}")
    print("COMPRESSOR END MAIN")

if __name__ == "__main__":
    main()
