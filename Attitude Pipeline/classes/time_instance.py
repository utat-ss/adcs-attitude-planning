
import numpy as np
from datetime import datetime


class timeInstance:
    """
    """

    #Intrinsic Properties (Direct from STK)
    date: datetime

    earth_vec: np.array[float]
    moon_vec: np.array[float]
    sun_vec: np.array[float]
    eclipsed: bool #Not intrinsic but not worth storing sunlight vector

    #Calculated Properties
    #WRT placement vector, defined in function call
    placement: np.array[float]
    #Stored in degrees
    earth_angle: float
    moon_angle: float
    sun_angle: float

    slew_rate: float #Defined only within an imaging_pass

    #Validation Checks
    checks: list[function]

    def __init__(self, date: datetime, earth_vec: list[float], moon_vec: list[float], 
                 sun_vec: list[float], sunlight_vec: list[float]) -> None:
        self.date = date
        self.earth_vec = np.array(earth_vec)
        self.moon_vec_vec = np.array(moon_vec)
        self.sun_vec = np.array(sun_vec)
        self.eclipsed = sunlight_vec[0] == 0 and sunlight_vec[1] == 0 and sunlight_vec[2] == 0

    def calculate_angles(self,placement: list[float]) -> None:
        self.placement = np.array(placement)
        self.earth_angle = timeInstance.ang_from_vecs(self.earth_vec, self.placement)
        self.moon_angle = timeInstance.ang_from_vecs(self.moon_vec, self.placement)
        self.sun_angle = timeInstance.ang_from_vecs(self.sun_vec, self.placement)

    def calculate_slew_rate(self, next_instance: timeInstance) -> None:
        delta_angle = timeInstance.ang_from_vecs(self.earth_vec, next_instance.earth_vec)
        delta_t = (self.date - next_instance.date).total_seconds()
        self.slew_rate = delta_angle/delta_t

    def set_default_checks(self) -> None:
        def sun_check(instance: timeInstance) -> bool:
            """Return True if instance satisfies sun constraint. (< 40 deg)"""
            return not (self.sun_angle < 40)

        def earth_check(instance: timeInstance, dist_to_earth=500)-> bool:
            """
            Return True if angle satisfies earth constraint.
            Check 40 deg cone intersection with 100 km atmosphere. (~110 deg)
            Source: https://www.researching.cn/articles/OJc35aead846202911
            """
            EARTH_RADIUS = 6371.0 #km
            atm_width = 100.0 #km
            sin_angle = (EARTH_RADIUS + atm_width)/(EARTH_RADIUS + dist_to_earth)
            sin_angle = max(min(sin_angle, 1), -1)
            earthlight_cone_angle = np.arcsin(sin_angle)  #δa=arcsin[(Er+d)/Es], from paper
            earthlight_cone_angle = np.rad2deg(earthlight_cone_angle)
            return not (instance.earth_angle < earthlight_cone_angle + 40)

        def moon_check(angle)-> bool:
            """
            Return True if angle violates moon constraint. (< 40 deg)
            """
            return not(self.moon_angle < 40)
        
        self.checks = [sun_check, earth_check, moon_check]


    def is_valid(self) -> bool:
        for check in self.checks:
            if not check(self):
                return False
        return True


    @classmethod
    def ang_from_vecs(v1: np.array[float], v2:np.array[float]) -> float:
        """Takes two vectors v1, v2 as numpy arrays and returns the angle between them in degrees"""
        normv1, normv2 = np.linalg.norm(v1), np.linalg.norm(v2)
        ang = np.arccos(np.dot(v1,v2)/ (normv1 * normv2))
        return np.rad2deg(ang)