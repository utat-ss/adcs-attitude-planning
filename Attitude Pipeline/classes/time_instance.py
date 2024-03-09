
import numpy as np
from datetime import datetime
from Checks.check import *


def ang_from_vecs(v1: np.array[float], v2:np.array[float]) -> float:
        """Takes two vectors v1, v2 as numpy arrays and returns the angle between them in degrees"""
        normv1, normv2 = np.linalg.norm(v1), np.linalg.norm(v2)
        ang = np.arccos(np.dot(v1,v2)/ (normv1 * normv2))
        return np.rad2deg(ang)

class TimeInstance:
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
    has_angles: bool

    slew_rate: float #Defined only within an imaging_pass
    has_slew: bool

    #Validation Checks
    checks: list[Check]

    def __init__(self, date: datetime, earth_vec: list[float], moon_vec: list[float], 
                 sun_vec: list[float], sunlight_vec: list[float]) -> None:
        self.date = date
        self.earth_vec = np.array(earth_vec)
        self.moon_vec_vec = np.array(moon_vec)
        self.sun_vec = np.array(sun_vec)
        self.eclipsed = sunlight_vec[0] == 0 and sunlight_vec[1] == 0 and sunlight_vec[2] == 0
        self.has_angles = False
        self.has_slew = False

    def calculate_angles(self,placement: list[float]) -> None:
        self.placement = np.array(placement)
        self.earth_angle = ang_from_vecs(self.earth_vec, self.placement)
        self.moon_angle = ang_from_vecs(self.moon_vec, self.placement)
        self.sun_angle = ang_from_vecs(self.sun_vec, self.placement)
        self.has_angles = True 

    def calculate_slew_rate(self, next_instance: TimeInstance) -> None:
        delta_angle = ang_from_vecs(self.earth_vec, next_instance.earth_vec)
        delta_t = (self.date - next_instance.date).total_seconds()
        self.slew_rate = delta_angle/delta_t
        self.has_slew = True

    def set_default_checks(self) -> None:
        self.checks = [SunCheck(), MoonCheck(), EarthCheck()]


    def is_valid(self) -> tuple[bool, str]:
        for check in self.checks:
            if not check.check_instance(self):
                return (False, check.error_msg)
        return (True, 'All Checks Passed')