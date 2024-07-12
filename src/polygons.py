import pandas as pd
import geopandas as gpd

def flood_alert_areas():
    """Function to build a gdf of flood warning areas (FWAs) from zipped shapefile"""

    # English FWA polys
    db = gpd.read_file("zip://data/Flood_Alert_Areas.zip/Flood_Alert_AreasPolygon.shp")
    db.columns = [c.upper() if c != "geometry" else c for c in db.columns]

    # Welsh FWA polys
    dbw = gpd.read_file("zip://data/NRW_FLOOD_ALERT.zip/NRW_FLOOD_ALERT.shp")
    dbw = dbw.drop(columns=[c for c in dbw.columns if c.startswith("W_")])

    db = pd.concat([db,dbw], axis=0)
    db.drop(columns=["PARENT"], inplace=True)

    return db

def flood_warning_areas():
    """Function to build a gdf of flood warning areas (FWAs) from zipped shapefile"""

    # English FWA polys
    db = gpd.read_file("zip://data/Flood_Warning_Areas.zip/Flood_Warning_AreasPolygon.shp")
    db.columns = [c.upper() if c != "geometry" else c for c in db.columns]

    # Welsh FWA polys
    dbw = gpd.read_file("zip://data/NRW_FLOOD_WARNING.zip/NRW_FLOOD_WARNING.shp")
    dbw = dbw.drop(columns=[c for c in dbw.columns if c.startswith("W_")])

    db = pd.concat([db,dbw], axis=0)
    db.drop(columns=["PARENT"], inplace=True)

    return db

# def flood_areas(): 
#     "Returns a gdf containing all flood areas whether severity 2 or 3"
#     # Dropped severity 3 (alerts) as not required 

#     # get flood alert areas
#     db1 = flood_alert_areas()

#     # get flood warning areas
#     db2 = flood_warning_areas()

#     # join
#     db1 = db1.append(db2)

#     return db1