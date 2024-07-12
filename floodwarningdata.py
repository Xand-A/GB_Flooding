""" This module provides an interface for extracting flood warning data
from JSON objects fetched from the Environment Agency API
"""

from .floodwarning import FloodWarning
from .datafetcher import fetch_flood_data, fetch_wales_data, fetch_scotland_data
from .stationdata import build_station_database, update_water_levels
from .stationdata import build_station_list, stations_by_river
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import numpy as np
import json
from datetime import datetime
import time
import os

# severity=3 for testing, severity=2 for production
severity = 2


def build_flood_list(use_cache=False):
    """Build a list of all flood events above a specified severity"""

    # probably want to focus on events with severity<=2
    data = fetch_flood_data(severity=severity, use_cache=use_cache)

    # initialize list of flood warnings
    flood_warnings = []

    # loop through the flood warning events
    for e in data["items"]:

        try:
            # Create flood warning object if all required data is
            # available, and add to list
            f = FloodWarning(
                message=e["message"],
                description=e["description"],
                flood_url=e["@id"],
                area_name=e["eaAreaName"],
                area_id=e["floodAreaID"],
                river_sea=e["floodArea"]["riverOrSea"],
                severity=e["severityLevel"],
                county=e["floodArea"]["county"],
                time_raised=e["timeRaised"],
                time_message_changed=e["timeMessageChanged"],
                time_severity_changed=e["timeSeverityChanged"],
            )

            flood_warnings.append(f)

        except:
            # Not all required data on the flood warning was available, so
            # skip
            print(
                "Not all of the data was available for flood {}".format(
                    e["description"]
                )
            )
            pass

    return flood_warnings


def build_flood_database(use_cache=False):
    """Build a dataframe containing all flood events above the
    specified severity
    """

    # fetch the JSON data
    data = fetch_flood_data(severity=severity, use_cache=use_cache)

    # set-up dataframe
    columns = [
        "flood_id",
        "description",
        "message",
        "area_name",
        "FWS_TACODE",
        "severity",
        "county",
        "river_or_sea",
        "time_raised",
        "time_message_changed",
        "time_severity_changed",
    ]

    db = pd.DataFrame(columns=columns)

    # loop through items in JSON to extract information
    for e in data["items"]:

        # get datetime objects from EA strings
        time_raised = datetime_from_string(e["timeRaised"])
        time_message_changed = datetime_from_string(e["timeMessageChanged"])
        time_severity_changed = datetime_from_string(e["timeSeverityChanged"])

        # populate row for one flood warning
        if "riverOrSea" in e["floodArea"].keys():
            riversea = e["floodArea"]["riverOrSea"]
        else:
            riversea = ""

        row = [
            e["@id"],
            e["description"],
            e["message"],
            e["eaAreaName"],
            e["floodAreaID"],
            e["severityLevel"],
            e["floodArea"]["county"],
            riversea,
            time_raised,
            time_message_changed,
            time_severity_changed,
        ]

        # append to dataframe
        db.loc[len(db)] = row

    # the same for Wales
    data = fetch_wales_data()

    # note the data is structured differently, and some fields are missing
    for e in data:

        time_raised = datetime_from_unix(e["TIMERAISED"])
        time_message_changed = datetime_from_unix(e["RIM_CHANGED"])
        time_severity_changed = datetime_from_unix(e["SEVERITY_CHANGED"])

        wales_area = "{} Wales".format(e["AREA"])

        # populate row for one flood warning
        row = [
            None,
            e["DESCRIPTION"],
            e["RIM_ENGLISH"],
            wales_area,
            e["FWACODE"],
            e["SEVERITYVALUE"],
            None,
            e["TIDAL"],
            time_raised,
            time_message_changed,
            time_severity_changed,
        ]

        db.loc[len(db)] = row

    return db


def build_scotland_geodataframe():

    # fetch scotland data
    data = fetch_scotland_data()
    sepa_areas = data["floodwarningMap"]["areas"]
    # convert to geodataframe
    sepa_df = GeoDataFrame(sepa_areas)

    def convert_geom(x):
        return np.array(x.split(","))

    # extract coordinates
    x = [convert_geom(sepa_areas[i]["x"]) for i in range(len(sepa_areas))]
    y = [convert_geom(sepa_areas[i]["y"]) for i in range(len(sepa_areas))]
    coords = []
    for p, q in zip(x, y):
        coords.append([(np.float32(n), np.float32(m)) for n, m in zip(p, q)])

    # create Polygons
    sepa_df = GeoDataFrame(sepa_areas, geometry=[Polygon(c) for c in coords])
    # only wart severity 2 warnings
    tmp = sepa_df.dropna(subset=["mtype"])
    tmp = tmp[tmp.mtype.str.contains("warning")]
    # align with current Eng/Wales dataframe
    tmp = tmp.drop(
        columns=["x", "y", "color", "fontColor", "borderColor", "click", "iType"]
    )
    sepa_df = GeoDataFrame()
    sepa_df["AREA"] = "Scotland: " + tmp.name
    sepa_df["FWS_TACODE"] = tmp.id
    sepa_df["TA_NAME"] = tmp.name
    sepa_df["DESCRIP"] = tmp.name
    sepa_df["description"] = tmp.name
    sepa_df["area_name"] = tmp.name
    sepa_df["severity"] = 2
    sepa_df["geometry"] = tmp.geometry
    sepa_df = sepa_df.set_geometry("geometry")

    return sepa_df


def update_flood_database(dt=15.0 * 60.0):
    """Updates the flood warning database every dt seconds
    --> 15 minutes = 15*60 seconds (default argument)

    The database is saved as a csv file and overwritten every
    dt seconds.
    """

    # start time
    starttime = time.time()
    datetime_string = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    # path and csv file name
    sub_dir = "/data/Geospatial/BenMcdermott/surge"
    filename = "flood_database" + datetime_string + ".csv"
    csv_file = os.path.join(sub_dir, filename)

    # initialise flood database
    db = build_flood_database()
    db["time"] = datetime.now()

    # get stations on rivers for each flood warning
    # stations_on_rivers = warning_station_levels()
    # db['stations_on_rivers'] = stations_on_rivers

    # write to file
    db.to_csv(csv_file)

    # infinite loop that waits dt seconds before next execution
    while True:
        # wait dt seconds before building the database
        # the modulus prevents drift as the following code executes
        time.sleep(dt - ((time.time() - starttime) % dt))

        # build new flood database and add current time attribute
        db = build_flood_database()
        db["time"] = datetime.now()

        # get stations on rivers for each flood warning
        # stations_on_rivers = warning_station_levels()
        # db['stations_on_rivers'] = stations_on_rivers

        # append csv file specifying mode 'a' and no header
        db.to_csv(csv_file, mode="a", header=False)


def datetime_from_string(datetime_string):
    """Returns a datetime object corresponding to the EA
    date + time string (e.g. time raised, time severity changed etc.)

    For one flood warning at a time.
    """

    year = int(datetime_string[:4])
    month = int(datetime_string[5:7])
    day = int(datetime_string[8:10])
    hour = int(datetime_string[11:13])
    minute = int(datetime_string[14:16])
    second = int(datetime_string[17:])

    return datetime(year, month, day, hour, minute, second)


def datetime_from_unix(unix_int):
    """Returns a datetime string from the unix timestamp provided by NRW"""
    ts = unix_int / 1000
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def warning_station_levels():
    """Returns a list of lists, each containing (river, MonitoringStation-s) tuples
    for each set of rivers corresponding to a flood warning.

    e.g. Flood warning --> rivers --> stations on each river
    """

    # build list of flood warnings
    flood_warnings = build_flood_list()

    # build list of monitoring stations + update levels
    stations = build_station_list()
    update_water_levels(stations)

    # match rivers with warnings to their monitoring stations
    stat_by_river = stations_by_river(stations)
    fw_river_stations = []
    for flood_warning in flood_warnings:
        # get separated list of rivers associated with flood warning
        # (possibly more than one!)
        rivers = flood_warning.river_sea.split(",")
        rivers_list = [s.strip() for s in rivers]

        # append list of stations on those rivers, else append None
        stations_on_river = [
            tuple([river, stat_by_river.get(river, None)]) for river in rivers_list
        ]
        fw_river_stations.append(stations_on_river)

    return fw_river_stations


def severity_changed(db):
    """Returns a list of [flood_id, Increased/ Decreased] lists based on
    whether the severity of a flood event has changed.
    """

    # get all stored flood ids
    fids = list(set(db.flood_id))

    # for each flood id, check if severity has changed
    fids_changed = []
    for fid in fids:
        # list of all severities for each flood id
        IY = db.flood_id == fid
        sev = list(db[IY].severity)

        # if severity has changed, append flood id to list
        if not all(x == sev[0] for x in sev):
            fids_changed.append(fid)
            break

    return fids_changed


def alerts_without_fwas(db, fwas):
    """Returns a dataframe containing active flood warning that do not have a corresponding
    FWA, with the current reference data.
    """

    alert_codes = list(db.FWS_TACODE)
    poly_codes = list(fwas.FWS_TACODE)

    codes = [code for code in alert_codes if code not in poly_codes]

    return db[db.FWS_TACODE.isin(codes)]

def build_dummy_flood_database():
    """Reads dummy set of flood warning data
    This is to be used in within live_flood_or_dummy function
    """
    df = pd.read_csv('floodwarningdummy.csv')

    return df


def live_flood_or_dummy():
    """Function to load in  live flood warnings, but if dataframe is empty (i.e. no flood warnings)
    function returns saved dummy data from Azure - used for demo / testing if no flood warnings active"""
    # Call the function to build flood gdf
    floods = build_flood_database()
    if len(floods) == 0:

        return build_dummy_flood_database()  # Placeholder for Azure data

    else:
        return floods