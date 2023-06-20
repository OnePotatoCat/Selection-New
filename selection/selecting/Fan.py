from .models import Fan as fn

class Fan_Cal(object):
    def __init__(self, fan_id :int):
        fan = fn.objects.get(pk = fan_id)
        self.model = fan.model
        self.size = fan.size
        
        self._rpm_coef = fan.rpm_coefficient
        self._pow_coef = fan.power_coefficient
        self._cur_coef = fan.current_coefficient

    def get_rpm(self) -> float:
        return self._rpm
    
    def get_power(self) -> float:
        return self._power

    def get_current(self) -> float:
        return self._current

    def set_properties(self, q :float, p :float) -> float:
        self.__set_rpm(q, p)
        self.__set_power(q, p)
        self.__set_current(q, p)

    def __set_rpm(self, q, p):
        # Output = rpm (rpm)
        self._rpm = self.__calculate_properties(q, p, self._rpm_coef)
        
    def __set_power(self, q, p):
        # Output = power (kW)
        self._power = self.__calculate_properties(q, p, self._pow_coef)/1000

    def __set_current(self, q, p):
        # Output = current (A)
        self._current = self.__calculate_properties(q, p, self._cur_coef)

    def __calculate_properties(self, q, p, c : list[float]) -> float:
        # q = airflow rate (m3/hr)
        # p = static pressure (Pa)
        output = c[0] * q + c[1] * p + \
                 c[2] * q**2 + c[3] * q * p + c[4] * p**2 + \
                 c[5] * q**3 + c[6] * q**2 * p + c[7] * q * p**2 + c[8] * p**3
        return output

def main():
    fan = Fan_Cal(1)
    fan.set_properties(6500,760)
    print(fan.get_rpm())
    print(fan.get_power())
    print(fan.get_current())
    print("FAN END")

if __name__ == "__main__":
    main()
