from datetime import datetime
from time_instance import TimeInstance

class imagingPass:
    """
    """

    instances: list[TimeInstance]
    time_range: tuple[datetime]

    def __init__(self, instances: list[TimeInstance]) -> None:
        self.instances = instances
        self.time_range = (instances[0].date, instances[-1].date)