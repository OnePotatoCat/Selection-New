from .Coil import Coil

class Evaporator_Cal(Coil):
    def __init__(self, evap_id :int) -> None:
        type = "evaporator"
        super().__init__(evap_id, type)

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