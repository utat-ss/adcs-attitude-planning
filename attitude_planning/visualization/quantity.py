import matplotlib.pyplot as plt
from enum import Enum
from ..tools.calculate import dist_between_lat_lon
from ..classes.simulation import Simulation

class Quantity(Enum):
    SCANLINE_ROTATION = "Scanline Rotation (degrees)"
    SCANLINE_INTERVAL = "Point Interval (m)"

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
    dates = [x[0] for x in values]
    values = [x[1] for x in values]
    # cut first 100 values
    dates = dates[200:]
    values = values[200:]
    plt.plot(dates, values)
    plt.xlabel("Date")
    plt.ylabel(quantity.value)
    plt.title(f"{quantity.value} vs Date")
    plt.show()


if __name__ == "__main__":
    from attitude_planning.tools.simulator import TensorTechSimulation, SimulatonConfig, Maneuver, AlignmentAxis
    sim = TensorTechSimulation.from_file("analysis/idr.json")
    simulation = Simulation.from_tensor_tech_sim(sim)
    simulation.derive_data()
    # plot_quantity(simulation, Quantity.SCANLINE_ROTATION)
    plot_quantity(simulation, Quantity.SCANLINE_INTERVAL)