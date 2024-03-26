from .Coil import Coil

class Evaporator_Cal(Coil):
    def __init__(self, evap_id :int) -> None:
        type = "evaporator"
        super().__init__(evap_id, type)
        

    def starting_dewpoint(self, vel :float, t_evap :float, t_inlet :float):
        c = self.start_dew_coef
        print(c)
        t_startdew = t_evap+ c[0] + c[1] * vel + c[2] * t_evap + c[3] * vel * t_evap + \
                    c[4] * t_inlet + c[5] * t_inlet * vel + c[6] * t_inlet * t_evap

        return t_startdew


def main():
    evap = Evaporator_Cal(1)
    print(evap.model)
    print(evap.dry_coef)
    print(evap.wet_coef)
    print(evap.min_airflow)
    print(evap.max_airflow)
    print(evap.U_dry(12,2.1))
    print(evap.U_wet(22,10,10,2.1))
    print("EVAP END MAIN")

if __name__ == "__main__":
    main()