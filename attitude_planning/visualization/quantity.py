import matplotlib.pyplot as plt
from enum import Enum
from ..tools.calculate import dist_between_lat_lon
from ..classes.simulation import Simulation

class Quantity(Enum):
    SCANLINE_ROTATION = "scanline_rotation"
    SCANLINE_INTERVAL = "scanline_interval"

def get_quantity(sim: Simulation, quantity: Quantity):
    values = []
    if quantity == Quantity.SCANLINE_ROTATION:
        values = [sim.llar[i][3] if sim.llar[i] else None for i in range(len(sim.llar))]
    elif quantity == Quantity.SCANLINE_INTERVAL:
        values = [None]
        for i in range(1, len(sim.llar)):
            if sim.llar[i] and sim.llar[i-1]:
                values.append(dist_between_lat_lon(sim.llar[i][0], sim.llar[i][1], sim.llar[i-1][0], sim.llar[i-1][1]))
            else:
                values.append(None)

    res = []
    for i in range(len(sim.dates)):
        if values[i] is not None:
            res.append((sim.dates[i], values[i]))
    
    return res

def plot_quantity(sim: Simulation, quantity: Quantity):
    values = get_quantity(sim, quantity)
    print(values)
    dates = [x[0] for x in values]
    values = [x[1] for x in values]
    plt.plot(dates, values)
    plt.show()


if __name__ == "__main__":
    from attitude_planning.tools.simulator import TensorTechSimulation, SimulatonConfig, Maneuver, AlignmentAxis
    sim = TensorTechSimulation.from_file("fixed_attitude_june_2024.json")
    simulation = Simulation.from_tensor_tech_sim(sim)
    simulation.derive_data()
    # plot_quantity(simulation, Quantity.SCANLINE_ROTATION)
    plot_quantity(simulation, Quantity.SCANLINE_INTERVAL)