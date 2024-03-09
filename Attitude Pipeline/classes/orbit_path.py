from imaging_pass import imagingPass
from time_instance import TimeInstance

class orbitPath:
    """
    """

    instances: list[TimeInstance]
    img_passes: list[imagingPass]

    def __init__(self, imaging_passes: list[imagingPass]) -> None:
        self.img_passes = imaging_passes
        self.instances = []
        for img_pass in imaging_passes:
            self.instances.extend(img_pass.instances)