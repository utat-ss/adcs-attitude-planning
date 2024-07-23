from ..tools.simulator import TensorTechSimulation
from ..tools.convert import mrp2quat
from ..tools.calculate import georef, vec_diff, mag
from datetime import datetime

class Simulation:
    attitude: list # Quaternions
    orbit: list # ECEF
    orbit_velocities: list
    orbit_speed: list
    dates: list # UTC
    star_tracker = [1, 0, 0]
    scanline_width_m = 20000
    scanline_height_m = 100
    integration_time_s = 0.032
    interpolation_time_s = 0.1

    # Derived Quantities
    llar: list # Lat, Lon, Alt, Roll

    def __init__(self, attitude, orbit, dates):
        self.attitude = attitude
        self.orbit = orbit
        self.dates = dates

    def timestep_s(self):
        return (self.dates[-1] - self.dates[0]).total_seconds() / len(self.dates)
    
    def interpolation_steps(self):
        return int(self.interpolation_time_s / self.timestep_s())

    def calculate_velocities(self): # TODO: This assumes constant time intervals
        self.orbit_velocities = [vec_diff(self.orbit[i], self.orbit[i-1]) for i in range(1, len(self.orbit))]
        self.orbit_velocities.append(self.orbit_velocities[-1])
        self.orbit_speed = [mag(v) for v in self.orbit_velocities]

    def derive_data(self):
        self.llar = [georef(self.orbit[i], self.attitude[i]) for i in range(len(self.orbit))]
        self.calculate_velocities()

    @classmethod
    def from_tensor_tech_sim(cls, sim: TensorTechSimulation):
        attitude = [mrp["val"] for mrp in sim.mrpData]
        attitude = [attitude[i:i+3] for i in range(0, len(attitude), 3)]
        attitude = [mrp2quat(m) for m in attitude]
        
        orbit = [sim.orbitData[i]["r"] for i in range(len(sim.orbitData))]
        dates = [sim.orbitData[i]["date"] for i in range(len(sim.orbitData))]
        dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in dates]
        return cls(attitude, orbit, dates)