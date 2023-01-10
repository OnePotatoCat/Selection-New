from Coil import Coil

class Evaporator(Coil):
    def __init__(self, model :str) -> None:
        type = "evaporator"
        super().__init__(model, type)
        self.evap_temp=0

def main():
    evap = Evaporator("es20")
    print(evap.dry_coef)
    print(evap.wet_coef)
    print(evap.min_airflow)
    print(evap.max_airflow)
    print(evap.U_dry(12,2.1))
    print(evap.U_wet(22,10,10,2.1))

if __name__ == "__main__":
    main()