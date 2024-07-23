import numpy as np

from pyquaternion import Quaternion
from attitude_planning.classes.simulation import Simulation

from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection='3d')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

colors = ['r', 'g', 'b']

lines = sum([ax.plot([], [], [], c=c)
             for c in colors], [])

startpoints = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
endpoints = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

ax.set_xlim((-8, 8))
ax.set_ylim((-8, 8))
ax.set_zlim((-8, 8))

ax.view_init(30, 0)

qs = []

def animate(i):
    q = qs[i]
    q = Quaternion(q)

    for line, start, end in zip(lines, startpoints, endpoints):
        start = q.rotate(start)
        end = q.rotate(end)

        line.set_data([start[0], end[0]], [start[1], end[1]])
        line.set_3d_properties([start[2], end[2]])

    fig.canvas.draw()
    return lines

def plot_attitude(simulation: Simulation):
    global qs
    qs = simulation.attitude
    anim = animation.FuncAnimation(fig, animate,
                                frames=len(simulation.attitude), interval=1, blit=False)
    # anim.save('example_attitude.mp4', fps=1)
    plt.show()

if __name__ == "__main__":
    from attitude_planning.tools.simulator import TensorTechSimulation
    sim = TensorTechSimulation.from_file("fixed_attitude_june_2024.json")
    simulation = Simulation.from_tensor_tech_sim(sim)
    simulation.derive_data()
    plot_attitude(simulation)