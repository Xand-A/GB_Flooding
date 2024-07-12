"""This module provides an interface for extracting station data
from JSON objects fetched from the Environment Agency API
"""

from .station import MonitoringStation
from .datafetcher import fetch_station_data, fetch_latest_water_level_data
from .utils import sorted_by_key
import pandas as pd
from collections import defaultdict
from haversine import haversine


def build_station_list(use_cache=True):
    """Build and return a list of all river level monitoring stations
    from data fetched from the EA. Each station is represented by a
    MonitoringStation object.

    Some data is unavailable or incomplete (see 'if' statements)
    """

    # fetch station data
    data = fetch_station_data(use_cache)

    # build list of MonitoringStation objects
    stations = []
    for e in data["items"]:
        # the town and river name are not always available
        town = None
        if "town" in e:
            town = e["town"]

        river = None
        if "riverName" in e:
            river = e["riverName"]

        # try to get the typical range (low,high)
        try:
            typical_range = (
                float(e["stageScale"]["typicalRangeLow"]),
                float(e["stageScale"]["typicalRangeHigh"]),
            )
        except:
            typical_range = None

        try:
            # create MonitoringStation object if all data is available,
            # and append to stations list

            s = MonitoringStation(
                station_id=e["@id"],
                measure_id=e["measures"][-1]["@id"],
                label=e["label"],
                coord=(float(e["lat"]), float(e["long"])),
                typical_range=typical_range,
                river=river,
                town=town,
            )

            stations.append(s)

        except:
            # not all data was available, so skip
            pass

    return stations


def update_water_levels(stations):
    """Attach water level data contained in 'data' (latest water levels)
    to MonitoringStation objects
    """

    # fetch level data
    data = fetch_latest_water_level_data()

    # dictionary relating the measure id to the latest reading (value)
    measure_id_to_value = dict()
    for measure in data["items"]:
        if "latestReading" in measure:
            latest_reading = measure["latestReading"]
            measure_id = latest_reading["measure"]
            measure_id_to_value[measure_id] = latest_reading["value"]

    # attach the latest reading to station objects
    for station in stations:

        # reset the latest level
        station.latest_level = None

        # attach new water level data (if available)
        if station.measure_id in measure_id_to_value and isinstance(
            measure_id_to_value[station.measure_id], float
        ):

            station.latest_level = measure_id_to_value[station.measure_id]


def build_station_database():
    """Builds a dataframe containing monitoring station data.
    Each row is one MonitoringStation object.
    """

    # get the list of MonitoringStation objects
    stations = build_station_list()

    # fetch the latest water levels
    update_water_levels(stations)

    # for each station, add a row to a pandas dataframe
    columns = [
        "station_id",
        "measure_id",
        "name",
        "coord",
        "typical_low",
        "typical_high",
        "river",
        "town",
        "latest_level",
    ]

    db = pd.DataFrame(columns=columns)

    for station in stations:
        if station.typical_range is not None:
            typ_low = station.typical_range[0]
            typ_high = station.typical_range[1]
        else:
            typ_low, typ_high = None, None

        row = [
            station.station_id,
            station.measure_id,
            station.name,
            station.coord,
            typ_low,
            typ_high,
            station.river,
            station.town,
            station.latest_level,
        ]

        db_length = len(db)
        db.loc[db_length] = row

    return db


def stations_by_river(stations):
    """Returns a dictionary that maps river name to a list of
    stations on the river
    """

    # Build dictionary (map) from river to monitoring stations
    river_to_stations = defaultdict(list)
    for station in stations:
        river_to_stations[station.river].append(station)

    return river_to_stations


def distance(p0, p1):
    """Return distance between two geographic coordinates (in km)"""
    return haversine(p0, p1)


def stations_by_distance(stations, p):
    """Return list of (station, distance) tuples, where 'distance' is the
    distance from the coordinate p. The list is sorted by distance.

    """

    # Build list of tuples (distance, station)
    stations_by_dist = []
    for station in stations:
        d = distance(p, station.coord)
        stations_by_dist.append((station, d))

    # Return list sorted by distance
    return sorted_by_key(stations_by_dist, 1)
