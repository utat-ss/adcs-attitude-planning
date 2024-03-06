from datetime import datetime
from time_instance import timeInstance

class imagingPass:
    """
    """

    instances: list[timeInstance]
    time_range: tuple[datetime]

    def __init__(self, instances: list[timeInstance]) -> None:
        self.instances = instances
        self.time_range = (instances[0].date, instances[-1].date)