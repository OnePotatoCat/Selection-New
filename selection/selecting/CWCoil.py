from abc import ABC, abstractmethod
from .models import Evaporator as evap
from .models import Condenser as cond

class CWCoil_Cal(ABC):
    def __init__(self, coil_id :str, type :str) -> None:

        pass


    def U_dry(self, dt :float, velocity :float) -> float:
        u = self.dry_coef[0] * velocity + self.dry_coef[1] * dt + self.dry_coef[2]*dt**2
        return u


    def U_wet(self, t_drybulb :float, t_dew :float, t_evap :float, velocity :float) -> float:
        u = self.wet_coef[0] + self.wet_coef[1] * t_dew + self.wet_coef[2] * t_drybulb + \
            self.wet_coef[3] * t_evap + self.wet_coef[4] * velocity + self.wet_coef[5] * t_evap * velocity + \
            self.wet_coef[6] * velocity / (t_drybulb - t_dew) + self.wet_coef[7] * (t_dew - t_evap) ** 2 + \
            self.wet_coef[8] * velocity * (t_dew - t_evap) ** 2
        return u
