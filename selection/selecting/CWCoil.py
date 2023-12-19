from abc import ABC, abstractmethod
from .models import ChillwaterCoil as cw_coil
from sklearn.linear_model import LinearRegression
import pickle
from .util import dry_input,wet_input,start_dew_input,dp_input

class CWCoil_Cal(ABC):
    def __init__(self, coil_id :str) -> None:
        coil = cw_coil.objects.get(pk=coil_id)
        self.model = coil.model
        self.surface_area = coil.area_surface
        self.frontal_area = coil.area_frontal
        self.udry_model = pickle.load(coil.udry_model)
        self.uwet_model = pickle.load(coil.uwet_model)
        self.mdry_model = pickle.load(coil.mdry_model)
        self.mwet_model = pickle.load(coil.mwet_model)
        self.starting_dewpoint_model = pickle.load(coil.starting_dewpoint)
        self.dp_model = pickle.load(coil.dp_model)
        self.min_airflow = coil.min_airflow
        self.max_airflow = coil.max_airflow


    def U_dry(self, vel :float, t_drybulb:float, t_in:float, t_out:float) -> float:
        return self.udry_model.predict(dry_input(vel, t_drybulb, t_in, t_out))[0]
        
    def U_wet(self, vel :float, t_drybulb:float, t_dewbulb:float, t_in:float, t_out:float) -> float:
        return self.uwet_model.predict(wet_input(vel, t_drybulb, t_dewbulb, t_in, t_out))[0]
    
    def starting_dewpoint(self, vel :float, t_drybulb :float, t_in :float, t_out :float):
        return self.starting_dewpoint_model.predict(start_dew_input(vel, t_drybulb, t_in, t_out))
    
    def mdot_dry(self, vel :float, t_drybulb:float, t_in:float, t_out:float) -> float:
        return self.mdry_model.predict(dry_input(vel, t_drybulb, t_in, t_out))[0]
    
    def mdot_wet(self, vel :float, t_drybulb:float, t_dewbulb:float, t_in:float, t_out:float) -> float:
        return self.mwet_model.predict(wet_input(vel, t_drybulb, t_dewbulb, t_in, t_out))[0]
    
    def pressure_drop(self, mdot :float) -> float:
        return self.dp_model.predict(dp_input(mdot))[0]