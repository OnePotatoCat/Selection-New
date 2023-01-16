from .Coil import Coil

class Condenser_Cal(Coil):
    def __init__(self, cond_id :int) -> None:
        type = "condenser"
        super().__init__(cond_id, type)


def main():
    cond = Condenser_Cal(1)
    print(cond.dry_coef)
    print(cond.U_dry(12, 3.0))
    print("COND END")


if __name__ == "__main__":
    main()