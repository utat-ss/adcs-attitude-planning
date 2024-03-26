from __future__ import annotations

from imaging_pass import ImagingPass
from time_instance import TimeInstance

class OrbitPath:
    """
    """

    instances: list[TimeInstance]
    img_passes: list[ImagingPass]

    def __init__(self, imaging_passes: list[ImagingPass]) -> None:
        self.img_passes = imaging_passes
        self.instances = []
        for img_pass in imaging_passes:
            self.instances.extend(img_pass.instances)

    @classmethod
    def construct_STK(cls, data: list[list[list]]) -> OrbitPath:
        passes = []
        
        for data_pass in data:
            img_pass = ImagingPass.construct_STK(data_pass)

        orbit = OrbitPath(passes)
        return orbit

    def fragment_passes(self) -> None:
        """ Fragment each imaging pass in the orbit into only those with all valid instances"""
        new_passes = []
        for img_pass in self.img_passes:
            new_passes.extend(img_pass.fragment_to_valid())

        self.img_passes = new_passes

    def get_num_partValid_passes(self) -> int:
        """ Return the number of imaging passes in the path that has at least one valid instance"""
        num = 0
        for img_pass in self.img_passes:
            if len(img_pass.find_valid_indicies()) > 0:
                num += 1
        return num
    
    def get_num_fullValid_passes(self) -> int:
        """ Return the number of imaging passes in the path that are fully valid"""
        num = 0
        for img_pass in self.img_passes:
            if len(img_pass.instances) == len(img_pass.find_valid_indicies()):
                num += 1
        return num
    
    def get_longest_imaging_pass(self) -> tuple[ImagingPass,tuple[int,int]]:
        """ Return the imaging pass that has the longest stretch of valid indicies and the start/end indicies of that stretch within the returned ImagingPass
        """
        longest_pass_len = 0
        for img_pass in self.img_passes:
            # Get the longest continuous stretch in the imaging pass
            fragments, fragment_endpoints = img_pass.fragment_to_valid()
            longest_fragment = fragments[0]
            for fragment, endpoints in zip(fragments, fragment_endpoints):
                if len(fragment.instances) > len(longest_fragment.instances):
                    longest_fragment = fragment
                    longest_fragment_endpoints = endpoints

            # Compare with previous biggest
            if len(longest_fragment.instances) > longest_pass_len:
                longest_pass = img_pass
                longest_endpoints = longest_fragment_endpoints
                longest_pass_len = len(longest_pass.instances)

        return longest_pass, longest_endpoints