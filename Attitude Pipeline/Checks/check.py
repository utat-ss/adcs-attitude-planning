from classes.time_instance import TimeInstance
import numpy as np

class Check:

    error_msg: str
    
    def __init__(self, message: str) -> None:
        self.error_msg = message

    def check_instance(self, instance: TimeInstance) -> bool:
        raise NotImplementedError



class SunCheck(Check):
    """Check if instance satisfies sun constraint. (tracker angle < 40 deg)"""
    def __init__(self) -> None:
        super().__init__('Sun Light Cone Check Failed.')

    def check_instance(self, instance: TimeInstance) -> bool:    
        return not (instance.sun_angle < 40)


class EarthCheck(Check):
    """ Check 40 deg cone intersection with 100 km atmosphere. (~110 deg)
        Source: https://www.researching.cn/articles/OJc35aead846202911 """
    
    dist_to_earth: float #km
    EARTH_RADIUS: float = 6371.0 #km
    atm_width: float = 100.0 #km

    def __init__(self) -> None:
        super().__init__('Earth Light Cone Check Failed.')
        self.dist_to_earth = 500 #km
        self.EARTH_RADIUS = 6371.0 #km
        self.atm_width = 100.0 #km

    def check_instance(self, instance: TimeInstance) -> bool:
        
        sin_angle = (self.EARTH_RADIUS + self.atm_width)/(self.EARTH_RADIUS + self.dist_to_earth)
        sin_angle = max(min(sin_angle, 1), -1)
        earthlight_cone_angle = np.arcsin(sin_angle)  #δa=arcsin[(Er+d)/Es], from paper
        earthlight_cone_angle = np.rad2deg(earthlight_cone_angle)
        return not (instance.earth_angle < earthlight_cone_angle + 40)


class MoonCheck(Check):
    """Check if instance satisfies moon constraint. (tracker angle < 40 deg)"""

    def __init__(self) -> None:
        super().__init__('Moon Light Cone Check Failed.')

    def check_instance(self, instance: TimeInstance) -> bool:    
        return not (instance.moon_angle < 40)