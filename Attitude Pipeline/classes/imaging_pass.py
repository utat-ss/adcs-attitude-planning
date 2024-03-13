from __future__ import annotations

from datetime import datetime
from time_instance import TimeInstance


class ImagingPass:
    """
    """

    instances: list[TimeInstance]
    time_range: tuple[datetime, datetime]
    
    placement: list[float]

    def __init__(self, instances: list[TimeInstance]) -> None:
        self.instances = instances
        self.time_range = (instances[0].date, instances[-1].date)

    @classmethod
    def construct_STK(cls, data: list[list]) -> ImagingPass:
        instances = []
        
        for data_instance in data:
            instance = TimeInstance.construct_STK(data_instance)

        img_pass = ImagingPass(instances)
        return img_pass

    def apply_placement(self, placement: list[float]):
        """ Given @placement, applies it to each TimeInstance in the pass. For each calculates the 
        relevant angles as well as the slew rates for each TimeInstance. Note: Slew rate of final instance is 0. 
        """
        self.placement = placement
        for i in range(len(self.instances) - 1):
            self.instances[i].calculate_angles(placement)
            self.instances[i].calculate_slew_rate(self.instances[i+1])
        self.instances[-1].calculate_angles(placement)
        self.instances[-1].slew_rate = 0

    def check_instances(self) -> bool:
        """Returns True if all instances in the pass are valid"""
        for instance in self.instances:
            if not instance.is_valid():
                return False
            
        return True

"""
    input 
    stk data
    choose imaging pass


    output
    lattitude
    longitude
    rotation: georeferencing 
"""