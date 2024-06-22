from .classes.simulation import Simulation
from .tools.simulator import TensorTechSimulation
from .tools.convert import ecef2lla

sim = TensorTechSimulation.from_file("analysis/fixed_attitude_june_2024.json")
sim = Simulation.from_tensor_tech_sim(sim)
sim.derive_data()

from .visualization.scanlines import animate_sim_lla
animate_sim_lla(sim)


# print(ecef2lla(-4782000.502831343834, -1862000.0526225355075, 3784000.946808165433))