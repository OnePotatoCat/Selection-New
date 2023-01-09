import os
import csv

class Compressor(object):
    def __init__(self, model :str) -> None:
        self.model = model
        path = os.getcwd()
        data_list = os.listdir(path)

        for data in data_list:
            filename = os.path.basename(data)
            if model in filename.lower():
                self.data =  data
                break

        self.cap_coef = self.__set_coefficient("capacity")
        self.pow_coef = self.__set_coefficient("power")
        self.cur_coef = self.__set_coefficient("current")
        self.mas_coef = self.__set_coefficient("mass flow")
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


    def __set_coefficient(self, property : str) -> list[float]:
        # property = "Capacity, Power, Current, Mass"
        with open(self.data, mode = 'r') as file:
            data = csv.reader(file) 
            for line in data:
                if not len(line):
                    continue
                if property in line[0].lower() and (line[1] != ''):
                    correct_line = line
                    break
        
        coefficient = []
        for i in range(1, len(correct_line)):
            coefficient.append(float(correct_line[i]))

        return coefficient  

    def __calculate_properties(self, t_evap, t_cond, c : list[float]) -> float:
        # t_evap = Evaporating Temperature (C)
        # t_cond = Condensing Temperature (C)
        # c = coefficient [0-9]
        output = c[0] + c[1] * t_evap + c[2] * t_cond + \
                c[3] * t_evap**2 + c[4] * t_evap * t_cond + c[5] * t_cond**2 + \
                c[6] * t_evap**3 + c[7] * t_evap**2 * t_cond + c[8] * t_evap * t_cond**2 + c[9] * t_cond**3
        return output


def main():
    compressor = Compressor("zr72kce")
    te = 10
    tc = 49
    compressor.set_properties(te, tc)
    print(f"Performance at Te={te} | Tc={tc}")
    print(f"Capacity = {round(compressor.get_capacity(),2)}")
    print(f"Power = {round(compressor.get_power(),2)}")
    print(f"Current = {round(compressor.get_current(),2)}")
    print(f"Massflow = {round(compressor.get_massflow(),2)}")
    

if __name__ == "__main__":
    main()
