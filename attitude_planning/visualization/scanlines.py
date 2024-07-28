import pandas as pd
import folium
from ..tools.calculate import make_scanline, add_dist_to_lat_lon
from ..classes.simulation import Simulation

def get_date_and_latlong(sim: Simulation):
    data = [[*sim.llar[i], sim.dates[i].strftime("%Y-%m-%d %H:%M:%S")] for i in range(len(sim.llar)) if sim.llar[i] is not None]
    data = [x for x in data if len(x) == 5]

    data = pd.DataFrame(data, columns=["lat", "lon", "alt", "roll", "date"])
    return data[["date", "lat", "lon", "roll"]]

def animate_sim_lla(sim: Simulation):
    data = get_date_and_latlong(sim)

def make_folium_rect(corners: list, opacity=1):
    return folium.Polygon(
        locations=[[lat, lon] for lat, lon in corners],
        color='blue',
        weight=1,
        fill=True,
        fill_color='blue',
        fill_opacity=opacity,
        opacity=opacity
    )

def add_scanline_to_map(m, lat, lon, next_lat, next_long, rot, width, height, integration_distance=0):
    corners = make_scanline(lat, lon,  next_lat, next_long, rot, width, height)
    int_time_corners = make_scanline(lat, lon, next_lat, next_long, rot, width, height + integration_distance) # TODO: Rotation currently wrt lat/long not orbit
    rect = make_folium_rect(corners)
    int_rect = make_folium_rect(int_time_corners, opacity=0.5)
    m.add_child(rect)
    m.add_child(int_rect)
    return m

def plot_scanlines(simulation: Simulation, start_index=0, end_index=2000):
    data = get_date_and_latlong(simulation)
    data = data[start_index:end_index]

    m = folium.Map(location=[data.iloc[0]["lat"], data.iloc[0]["lon"]], zoom_start=6, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
    for i in range(len(data) - 1):
        lat = data.iloc[i]["lat"]
        lon = data.iloc[i]["lon"]
        next_lat = data.iloc[i+1]["lat"]
        next_long = data.iloc[i+1]["lon"]
        rot = data.iloc[i]["roll"]
        int_dist = simulation.integration_time_s * simulation.orbit_speed[i]
        m = add_scanline_to_map(m, lat, lon, next_lat, next_long, rot, simulation.scanline_width_m, simulation.scanline_height_m, int_dist)
    
    # Display the map
    m.save("map.html")
    import webbrowser
    import os
    webbrowser.open_new_tab("file://" + os.path.join(os.getcwd(), "map.html"))

if __name__ == "__main__":
    from attitude_planning.tools.simulator import TensorTechSimulation
    sim = TensorTechSimulation.from_file("analysis/idr.json")
    simulation = Simulation.from_tensor_tech_sim(sim)
    simulation.derive_data()
    data = get_date_and_latlong(simulation)
    data = data[20000:22000]

    m = folium.Map(location=[data.iloc[0]["lat"], data.iloc[0]["lon"]], zoom_start=6, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
    for i in range(len(data) - 1):
        lat = data.iloc[i]["lat"]
        lon = data.iloc[i]["lon"]
        next_lat = data.iloc[i+1]["lat"]
        next_long = data.iloc[i+1]["lon"]
        rot = data.iloc[i]["roll"]
        int_dist = simulation.integration_time_s * simulation.orbit_speed[i]
        m = add_scanline_to_map(m, lat, lon, next_lat, next_long, rot, simulation.scanline_width_m, simulation.scanline_height_m, int_dist)
    
    # Display the map
    m.save("map.html")
    import webbrowser
    import os
    webbrowser.open_new_tab("file://" + os.path.join(os.getcwd(), "map.html"))