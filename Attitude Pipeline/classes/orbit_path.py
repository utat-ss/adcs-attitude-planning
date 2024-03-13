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
