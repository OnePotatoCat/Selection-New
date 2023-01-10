from abc import ABC, abstractmethod
import os
import csv
import numpy as np

class Coil(ABC):
    def __init__(self, model :str, type :str) -> None:
        self.type = type
        self.model = model
        path = os.getcwd() + "\\Coil"
        data_list = os.listdir(path)

        for data in data_list:
            filename = os.path.basename(data)
            if type in filename.lower():
                self.data =  path +"\\" + data 
                break

        self.dry_coef = []
        self.wet_coef = []
        self.surface_area = 0
        self.frontal_area = 0
        self.__get_coefficient()
        pass


    def __get_coefficient(self):
        with open(self.data, mode = 'r') as file:
            data = csv.reader(file)
            for line in data:
                if self.model in line[0]:
                    self.surface_area= float(line[1])
                    self.frontal_area= float(line[2])
                    self.dry_coef = np.array(line[3:6]).astype(float)
                    if (self.type == "evaporator"):
                        self.wet_coef = np.array(line[6:]).astype(float)
                        self.min_airflow = float(line[15])
                        self.max_airflow = float(line[16])
                    break


    def U_dry(self, dt :float, velocity :float) -> float:
        u = self.dry_coef[0] * velocity + self.dry_coef[1] * dt + self.dry_coef[2]*dt**2
        return u


    def U_wet(self, t_drybulb :float, t_dew :float, t_evap :float, velocity :float) -> float:
        u = self.wet_coef[0] + self.wet_coef[1] * t_dew + self.wet_coef[2] * t_drybulb + \
            self.wet_coef[3] * t_evap + self.wet_coef[4] * velocity + self.wet_coef[5] * t_evap * velocity + \
            self.wet_coef[6] * velocity / (t_drybulb - t_dew) + self.wet_coef[7] * (t_dew - t_evap) ** 2 + \
            self.wet_coef[8] * velocity * (t_dew - t_evap) ** 2
        return u
