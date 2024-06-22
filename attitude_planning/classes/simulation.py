from ..tools.simulator import TensorTechSimulation
from ..tools.convert import mrp2quat
from ..tools.calculate import georef
from datetime import datetime

class Simulation:
    attitude: list # Quaternions
    orbit: list # ECEF
    dates: list # UTC

    # Derived Quantities
    llar: list # Lat, Lon, Alt, Roll

    def __init__(self, attitude, orbit, dates):
        self.attitude = attitude
        self.orbit = orbit
        self.dates = dates

    def derive_data(self):
        self.llar = [georef(self.orbit[i], self.attitude[i]) for i in range(len(self.orbit))]

    @classmethod
    def from_tensor_tech_sim(cls, sim: TensorTechSimulation):
        attitude = [mrp["val"] for mrp in sim.mrpData]
        attitude = [attitude[i:i+3] for i in range(0, len(attitude), 3)]
        attitude = [mrp2quat(m) for m in attitude]
        
        orbit = [sim.orbitData[i]["r"] for i in range(len(sim.orbitData))]
        dates = [sim.orbitData[i]["date"] for i in range(len(sim.orbitData))]
        dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in dates]
        return cls(attitude, orbit, dates)