from Coil import Coil

class Condenser(Coil):
    def __init__(self, model :str) -> None:
        type = "condenser"
        super().__init__(model, type)


def main():
    cond = Condenser(1)
    print(cond.dry_coef)
    print(cond.U_dry(12, 3.0))


if __name__ == "__main__":
    main()