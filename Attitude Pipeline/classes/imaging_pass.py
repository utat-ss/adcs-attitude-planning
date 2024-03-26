from __future__ import annotations

from datetime import datetime

from numpy import indices
from time_instance import TimeInstance


class ImagingPass:
    """
    """

    instances: list[TimeInstance]
    time_range: tuple[datetime, datetime]
    
    placement: list[float]

    #Constructor Methods
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


    def apply_placement(self, placement: list[float], final_slew: float = 0):
        """ Given @placement of the star tracker, applies it to each TimeInstance in the pass. For each calculates the 
        relevant angles as well as the slew rates for each TimeInstance. Note: Slew rate of final instance is 0 unless specified. 
        """
        self.placement = placement
        for i in range(len(self.instances) - 1):
            self.instances[i].calculate_angles(placement)
            self.instances[i].calculate_slew_rate(self.instances[i+1])
        self.instances[-1].calculate_angles(placement)
        self.instances[-1].slew_rate = final_slew

    def find_valid_indicies(self) -> list[int]:
        """Returns list of indices for self.instances of valid instances""" 
        indicies = []
        for i in range(len(self.instances)):
            if self.instances[i].is_valid():
                indicies.append(i)

        return indicies

    def find_valid_instances(self) -> list[TimeInstance]:
        """Returns list of all valid instances in the pass"""
        instances = []
        for instance in self.instances:
            if instance.is_valid():
                instances.append(instance)
            
        return instances
    
    def fragment_to_valid(self) -> tuple[list[ImagingPass], list[tuple[int,int]]]:
        """Returns a list of new Imaging passes, each of which has all consecutive valid indicies.
         Each returned imaging pass' instances are a subset of self.instances.
         Also returns the start and ending indicies of each fragment w.r.t self.instances, ex. [(3,23), (25, 56), ...]
         If no instances in self are valid, return empty lists."""
        valid_indicies = self.find_valid_indicies()
        if len(valid_indicies) == 0:
            return [], []
        
        # Collect valid indicies into continuous stretches
        pass_indices: list[list[int]] = []
        curr_indicies: list[int] = []
        curr_indicies.append(valid_indicies[0])
        for index in valid_indicies[1:]:
            if curr_indicies[-1] == index - 1:
                curr_indicies.append(index)
            else:
                pass_indices.append(curr_indicies)
                curr_indicies = [index]

        # Turn indicies into ImagingPass objects
        passes = []
        for fragment in pass_indices:
            pass_obj = ImagingPass(self.instances[fragment[0]:fragment[-1]])
            pass_obj.apply_placement(self.placement, self.instances[fragment[-1]].slew_rate)
            passes.append(pass_obj)

        # Extract just the start and end indicies
        indicies = [(frag[0], frag[-1]) for frag in pass_indices]

        return passes, indicies
    

"""
    input 
    stk data
    choose imaging pass


    output
    lattitude
    longitude
    rotation: georeferencing 
"""