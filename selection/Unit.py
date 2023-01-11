from Evaporator import Evaporator
from Condenser import Condenser
from Fan import Fan
from Compressor import Compressor
import os
import csv
import numpy as np

class Unit(object):
    def __init__(self, model :str, esp :float, filter_type :str) -> None:
        # model = unit model
        # filter type = G4 , F7
        self.model = model
        self.esp = esp
        self.outlet_temp = 0
        self.outlet_rh = 0
        self.filter_type = filter_type
        path = os.getcwd()
        data_list = os.listdir(path)

        for data in data_list:
            filename = os.path.basename(data)
            if "unit" in filename.lower():
                self.data =  data
                break
        
        self.__get_data()
        self.total_capacity = 0
        self.sensible_capacity = 0

    def __get_data(self):
        with open(self.data, mode = 'r') as file:
            data = csv.reader(file)
            for line in data:
                if self.model in line[0]:
                    self.evaporator = Evaporator(line[1])
                    self.condenser = Condenser(line[2])
                    self.compressor = Compressor(line[3])
                    self.fan = Fan(line[4])
                    self.no_of_fan = int(line[5])
                    self.isp_g4 = np.array(line[7:10]).astype(float)
                    self.isp_f7 = np.array(line[10:]).astype(float)
                    return
            raise Exception(f"Invalid unit model name, {self.model}")


    def __get_isp(self, airflow :float) -> float:
        if self.filter_type == "g4":
            c = self.isp_g4
            self._isp = c[0] + c[1]*airflow + c[2]*airflow**2
        elif self.filter_type == "f7":
            c = self.isp_f7
            self._isp = c[0] + c[1]*airflow + c[2]*airflow**2
        else:
            raise Exception(f"Invalid filter type, {self.filter_type}.")
        
        return self._isp
    

    def get_tsp(self, airflow:float) -> float:
        self.airflow = airflow
        self.tsp = self.esp + self.__get_isp(airflow)
        return self.tsp


def main():
    unit = Unit("esu20aes", 50,"g4")
    print(unit.evaporator.model)
    print(unit.condenser.model)
    print(unit.compressor.model)
    print(unit.fan.model)
    print(unit.get_tsp(6500))
    print(unit.fan.set_properties(6500/unit.no_of_fan,unit.get_tsp(6500)))

if __name__ == "__main__":
    main()
