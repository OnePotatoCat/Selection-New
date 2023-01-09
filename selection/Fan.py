import os
import csv
import numpy as np

class Fan(object):
    def __init__(self, model :str):
        self.model = model
        path = os.getcwd()
        data_list = os.listdir(path)

        for data in data_list:
            filename = os.path.basename(data)
            if "fan" in filename.lower():
                self.data =  data
                break
        
        self.rpm_coef = []
        self.pow_coef = []
        self.cur_coef = []
        self.__set_coefficient()

    def get_rpm(self) -> float:
        return self._rpm
    
    def get_power(self) -> float:
        return self._power

    def get_current(self) -> float:
        return self._current

    def set_properties(self, q :float, p :float) -> float:
        self.__set_capacity(q, p)
        self.__set_power(q, p)
        self.__set_current(q, p)

    def __set_capacity(self, q, p):
        # Output = rpm (rpm)
        self._rpm = self.__calculate_properties(q, p, self.rpm_coef)
        
    def __set_power(self, q, p):
        # Output = power (kW)
        self._power = self.__calculate_properties(q, p, self.pow_coef)

    def __set_current(self, q, p):
        # Output = current (A)
        self._current = self.__calculate_properties(q, p, self.cur_coef)


    def __set_coefficient(self):
        # property = "Capacity, Power, Current, Mass"
        with open(self.data, mode = 'r') as file:
            data = csv.reader(file)
            for line in data:
                if self.model in line[0]:
                    self.rpm_coef = np.array(line[1:10]).astype(float)
                    self.pow_coef = np.array(line[10:19]).astype(float)
                    self.cur_coef = np.array(line[19:]).astype(float)
                    break
        

    def __calculate_properties(self, q, p, c : list[float]) -> float:
        # q = airflow rate (m3/hr)
        # p = static pressure (Pa)
        output = c[0] * q + c[1] * p + \
                 c[2] * q**2 + c[3] * q * p + c[4] * p**2 + \
                 c[5] * q**3 + c[6] * q**2 * p + c[7] * q * p**2 + c[8] * p**3
        return output

def main():
    fan = Fan("r3g560fa2803")
    fan.set_properties(6500,760)
    print(fan.get_rpm())
    print(fan.get_power())
    print(fan.get_current())
    

if __name__ == "__main__":
    main()
