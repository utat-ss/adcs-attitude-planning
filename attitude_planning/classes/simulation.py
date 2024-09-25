from ..tools.simulator import TensorTechSimulation
from ..tools.convert import mrp2quat
from ..tools.calculate import georef, vec_diff, mag, interpolate_orbit, interpolate_attitude, interpolate_dates
from datetime import datetime

class Simulation:
    attitude: list # Quaternions
    orbit: list # ECEF
    orbit_velocities: list
    orbit_speed: list
    dates: list # UTC
    sun_vector: list # ECEF
    star_tracker = [1, 0, 0]
    imaging_site_location = [0, 0] # Lat, Lon
    imaging_attitude: list # Quaternions or None
    is_site_visible: list # Boolean
    scanline_width_m = 20000
    scanline_height_m = 100
    integration_time_s = 1/60
    interpolation_time_s = 1/60 # 60 Hz camera

    # Derived Quantities
    llar: list # Lat, Lon, Alt, Roll

    def __init__(self, attitude, orbit, dates):
        self.attitude = attitude
        self.orbit = orbit
        self.dates = dates

    def timestep_s(self):
        return (self.dates[-1] - self.dates[0]).total_seconds() / len(self.dates)
    
    def interpolation_steps(self):
        return int(self.timestep_s() / self.interpolation_time_s)
    
    def interpolate(self):
        self.attitude = interpolate_attitude(self.attitude, self.interpolation_steps())
        self.orbit = interpolate_orbit(self.orbit, self.interpolation_steps())
        self.dates = interpolate_dates(self.dates, self.interpolation_steps())

    def calculate_velocities(self): # TODO: This assumes constant time intervals
        self.orbit_velocities = [vec_diff(self.orbit[i], self.orbit[i-1]) for i in range(1, len(self.orbit))]
        self.orbit_velocities.append(self.orbit_velocities[-1])
        self.orbit_speed = [mag(v)/self.timestep_s() for v in self.orbit_velocities]

    def calculate_sun_vector(self):
        # Use dates to find sun vector
        self.sun_vector = []

    def calculate_imaging_attitude(self):
        # From the orbit (self.orbit) and imaging site (self.imaging_site_location), calculate the imaging attitude. Also check whether the site is visible (we don't look through the earth)
        self.imaging_attitude = []
        self.is_site_visible = []

    def derive_data(self):
        self.interpolate()
        self.llar = [georef(self.orbit[i], self.attitude[i]) for i in range(len(self.orbit))]
        self.calculate_velocities()
        self.calculate_sun_vector()
        self.calculate_imaging_attitude()

    @classmethod
    def from_tensor_tech_sim(cls, sim: TensorTechSimulation):
        attitude = [mrp["val"] for mrp in sim.mrpData]
        attitude = [attitude[i:i+3] for i in range(0, len(attitude), 3)]
        attitude = [mrp2quat(m) for m in attitude]
        
        orbit = [sim.orbitData[i]["r"] for i in range(len(sim.orbitData))]
        dates = [sim.orbitData[i]["date"] for i in range(len(sim.orbitData))]
        dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in dates]
        return cls(attitude, orbit, dates)