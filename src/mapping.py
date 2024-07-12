import folium
from folium.plugins import Fullscreen
import geopandas

def generate_basemap():
    #location point
    centre_of_uk = (53.82, -2.41)

    # basemap
    m = folium.map(
        location = centre_of_uk,
        tiles = "OpenStreetMap",
        zoom_start = 7,
        control_scale = True,
        prefer_canvas=True,
    )

    # add full screen button
    Fullscreen(
        title="Expand me", title_cancel="Exit fullscreen", force_seperate_button=True 
    )

def map_data(db):
    db["geoid"] = db.index.astype(str)
    plot_cols = [
        "geoid",
        "FWS_TACODE",
        "severity",
        "description",
        "message",
        "geom",
    ]

    data = db[plot_cols].sort_values(by=["severity"], ascending = True)
