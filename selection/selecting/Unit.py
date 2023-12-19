from .Evaporator import Evaporator_Cal as evap
from .Condenser import Condenser_Cal as cond
from .Fan import Fan_Cal as fn
from .Compressor import Compressor_Cal as comp
from .CWCoil import CWCoil_Cal as cw
from .models import Unit as unit_obj

class Unit_Cal(object):
    # def __init__(self, unit_id :int,
    #              evap_id :int, cond_id :int,
    #              comp_id :int, fan_id :int,
    #              esp :float, filter_type :str) -> None:

    #     unit = unit_obj.objects.get(pk = unit_id)
    #     self.model = unit.model
    #     self.evaporator = evap(evap_id)
    #     self.condenser = cond(cond_id)
    #     self.compressor = comp(comp_id)
    #     self.no_of_comp = unit.number_of_compressor
        
    #     self.fan = fn(fan_id)
    #     self.no_of_fan = unit.number_of_fan
    #     self._isp_g4_coef = unit.g4_static_coefficient
    #     self._isp_f7_coef = unit.f7_static_coefficient

    #     self.esp = esp
    #     self.filter_type = filter_type

    #     self.outlet_temp = 0
    #     self.outlet_rh = 0
    #     self.total_capacity = 0
    #     self.sensible_capacity = 0

    def __init__(self, unit_id :int,
                    evap_id :int, 
                    cond_id :int,
                    comp_id :int, 
                    cw_id :int,
                    fan_id :int,
                    esp :float, filter_type :str) -> None:

        unit = unit_obj.objects.get(pk = unit_id)
        self.model = unit.model
        if (evap_id):
            self.evaporator = evap(evap_id)
        if (cond_id):
            self.condenser = cond(cond_id)
        if (comp_id):
            self.compressor = comp(comp_id)
        if (cw_id):
            self.cw = cw(cw_id)
        self.no_of_comp = unit.number_of_compressor
        
        self.fan = fn(fan_id)
        self.no_of_fan = unit.number_of_fan
        self._isp_g4_coef = unit.g4_static_coefficient
        self._isp_f7_coef = unit.f7_static_coefficient

        self.esp = esp
        self.filter_type = filter_type

        self.outlet_temp = 0
        self.outlet_rh = 0
        self.total_capacity = 0
        self.sensible_capacity = 0

    # contructor for DX unit
    @classmethod
    def as_dx(cls, unit_id :int,
              evap_id :int, 
              cond_id :int,
              comp_id :int, 
              fan_id :int,
              esp :float, filter_type :str) ->None:
        instance = cls(unit_id, evap_id, cond_id, comp_id, None, fan_id, esp, filter_type)
        return instance

    # contructor for CW unit
    @classmethod
    def as_cw(cls, unit_id :int,
              cw_id :int, 
              fan_id :int,
              esp :float, filter_type :str) ->None:
        instance = cls(unit_id, None, None, None, cw_id, fan_id, esp, filter_type)
        return instance


    def get_isp(self, airflow :float) -> float:
        if self.filter_type == "g4":
            c = self._isp_g4_coef
            self._isp = c[0] + c[1]*airflow + c[2]*airflow**2
        elif self.filter_type == "f7":
            c = self._isp_f7_coef
            self._isp = c[0] + c[1]*airflow + c[2]*airflow**2
        else:
            raise Exception(f"Invalid filter type, {self.filter_type}.")
        
        return self._isp
    

    def get_tsp(self, airflow:float) -> float:
        self.airflow = airflow
        self.tsp = self.esp + self.get_isp(airflow)
        return self.tsp


def main():
    unit = Unit_Cal(1, 1, 1, 1, 1, 50,"g4")
    print(unit.evaporator.model)
    print(unit.condenser.model)
    print(unit.compressor.model)
    print(unit.fan.model)
    print(unit.get_tsp(6500))
    print(unit.fan.set_properties(6500/unit.no_of_fan,unit.get_tsp(6500)))

if __name__ == "__main__":
    main()
