import pandas as pd
import plotly.express as px
from ..classes.simulation import Simulation

def animate_sim_lla(sim: Simulation):
    data = [[*sim.llar[i], sim.dates[i].strftime("%Y-%m-%d %H:%M:%S")] for i in range(len(sim.llar)) if sim.llar[i] is not None]
    data = [x for x in data if len(x) == 5]
    data = pd.DataFrame(data, columns=["lat", "lon", "alt", "roll", "date"])
    data_ll_only = data[["lat", "lon"]]
    center = data_ll_only.mean().to_dict()
    center_lat = center["lat"]
    center_lon = center["lon"]

    fig = px.scatter_mapbox(data, lat="lat", lon="lon", color_discrete_sequence=["fuchsia"], zoom=3, animation_frame="date")
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker=dict(size=12))
    fig.update_geos(center=dict(lat=center_lat, lon=center_lon))
    fig.show()