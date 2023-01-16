from .models import Compressor as comp

class Compressor_Cal(object):
    def __init__(self, comp_id :int) -> None:
        compressor = comp.objects.get(pk = comp_id)
        self.model = compressor.model
        self.cap_coef = compressor.capacity_coefficient
        self.pow_coef = compressor.power_coefficient
        self.cur_coef = compressor.current_coefficient
        self.mas_coef = compressor.current_coefficient
        self.set_properties(10,45)
    
    def get_capacity(self) -> float:
        return self._capacity

    def get_power(self) -> float:
        return self._power

    def get_current(self) -> float:
        return self._current
    
    def get_massflow(self) -> float:
        return self._massflow

    def set_properties(self, t_evap :float, t_cond :float) -> float:
        self.__set_capacity(t_evap, t_cond)
        self.__set_power(t_evap, t_cond)
        self.__set_current(t_evap, t_cond)
        self.__set_massflow(t_evap, t_cond)


    def __set_capacity(self, t_evap, t_cond):
        # Output = Cooling Capacity (kW)
        self._capacity = self.__calculate_properties(t_evap, t_cond, self.cap_coef)

    def __set_power(self, t_evap, t_cond):
        # Output = Power Input (kW)
        self._power = self.__calculate_properties(t_evap, t_cond, self.pow_coef)

    def __set_current(self, t_evap, t_cond):
        # Output = Current (A)
        self._current = self.__calculate_properties(t_evap, t_cond, self.cur_coef)

    def __set_massflow(self, t_evap, t_cond):
        # Output = Massflow Rate (kg/s)
        self._massflow = self.__calculate_properties(t_evap, t_cond, self.mas_coef)  


    def __calculate_properties(self, t_evap, t_cond, c : list[float]) -> float:
        # t_evap = Evaporating Temperature (C)
        # t_cond = Condensing Temperature (C)
        # c = coefficient [0-9]
        output = c[0] + c[1] * t_evap + c[2] * t_cond + \
                c[3] * t_evap**2 + c[4] * t_evap * t_cond + c[5] * t_cond**2 + \
                c[6] * t_evap**3 + c[7] * t_evap**2 * t_cond + c[8] * t_evap * t_cond**2 + c[9] * t_cond**3
        return output


def main():
    compressor = Compressor_Cal(1)
    te = 10
    tc = 49
    compressor.set_properties(te, tc)
    print(f"Performance at Te={te} | Tc={tc}")
    print(f"Capacity = {round(compressor.get_capacity(),2)}")
    print(f"Power = {round(compressor.get_power(),2)}")
    print(f"Current = {round(compressor.get_current(),2)}")
    print(f"Massflow = {round(compressor.get_massflow(),2)}")
    print("COMPRESSOR END MAIN")

if __name__ == "__main__":
    main()
