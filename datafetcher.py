"""This module provides functionality for retreiving real-time and
latest flood warning data"""

import os
import json
import requests
from bs4 import BeautifulSoup

from .azure_setup import (
    NRW_API_key,
)

sub_dir = "cache"

def fetch(url, headers={}):
    """Fetch data from url and return fetched JSON object"""
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def dump(data, filename):
    """Save JSON object to file"""
    f = open(filename, "w")
    data = json.dump(data, f)


def load(filename):
    """Load JSON object from file"""
    f = open(filename, "r")
    data = json.load(f)
    return data


def fetch_flood_data(severity=2, use_cache=False):
    """Fetch data from Environment agency for all areas with a
    severity worse than 2 via a REST API and return retrieved
    data as a JSON object.

    Fetched data is dumped to a cache file so on subsequent call it
    can optionally be retrieved from the cache file. This is faster
    than retrieval over the Internet and avoids excessive calls to the
    Environment Agency service.

    """

    # URL for retrieving data for active stations with river level
    # monitoring (see http://environment.data.gov.uk/flood-monitoring/doc/reference)
    root_url = "https://environment.data.gov.uk/flood-monitoring/"
    url = "{root_url}id/floods?min-severity={severity}".format(
        root_url=root_url, severity=severity
    )

    try:
        os.makedirs(sub_dir)
    except:
        pass
    cache_file = os.path.join(sub_dir, "flood_warning_data.json")

    # Attempt to load station data from cache file, otherwise fetch over
    # Internet
    if use_cache:
        try:
            # Attempt to load from file
            data = load(cache_file)
        except:
            # If load from file fails, fetch and dump to file
            data = fetch(url)
            dump(data, cache_file)
    else:
        # Fetch and dump to file
        data = fetch(url)
        dump(data, cache_file)

    return data


def fetch_wales_data(severity=2, use_cache=False):
    
    url = 'https://api.naturalresources.wales/floodwarnings/v3/all'
    headers = {'Ocp-Apim-Subscription-Key': 
               NRW_API_key}
    
    cache_file = os.path.join(sub_dir, 'wales_flood_warning_data.json')

    # Attempt to load station data from cache file, otherwise fetch over
    # Internet
    if use_cache:
        try:
            # Attempt to load from file
            data = load(cache_file)
        except:
            # If load from file fails, fetch and dump to file
            data = fetch(url, headers=headers)
            dump(data, cache_file)
    else:
        # Fetch and dump to file
        data_json = fetch(url, headers=headers)
        # strip out unwanted parts of the JSON dict and return a list of features
        data = []
        for item in data_json['features']:
            # keep only those items with a severity less than or equal to 'severity'
            if item['properties']['SEVERITYVALUE'] <= 2:
                data.append(item['properties'])
        dump(data, cache_file)

    return data


def fetch_scotland_data():

    url = "https://floodline.sepa.org.uk/floodupdates/#tabset-tab-2"
    #r = requests.get(url, proxies=proxy_dict)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    script_list = soup.find_all("script")
    script_list = [str(s) for s in script_list]
    poly_string = [s for s in script_list if "jQuery.extend" in s][0]
    ix = poly_string.find("{ ")
    iy = poly_string.rfind(")")
    poly_string = poly_string[ix:iy]

    return json.loads(poly_string)


def ea_monitoring(severity=2):
    """Function to monitor if there are any active flood warnings at the
    current time. Returns 'True' if there are warnings, 'False' if there are
    no warnings.
    """

    root_url = "https://environment.data.gov.uk/flood-monitoring/"
    url = "{root_url}id/floods?min-severity={severity}".format(
        root_url=root_url, severity=severity
    )
    data = fetch(url)

    return bool(data["items"])


def fetch_station_data(use_cache=True):
    """Fetch data from Environment agency for all active river level
    monitoring stations via a REST API and return retrieved data as a
    JSON object.

    Fetched data is dumped to a cache file so on subsequent call it
    can optionally be retrieved from the cache file. This is faster
    than retrieval over the Internet and avoids excessive calls to the
    Environment Agency service.
    """

    # URL for retreiving data from active river level monitoring
    # stations
    root_url = "http://environment.data.gov.uk/flood-monitoring/"
    url = (
        root_url
        + "id/stations?status=Active&parameter=level&qualifier=Stage&_view=full"
    )

    try:
        os.makedirs(sub_dir)
    except:
        pass

    cache_file = os.path.join(sub_dir, "station_data.json")

    # attempt to read data from file, otherwise fetch from URL
    if use_cache:
        try:
            data = load(cache_file)
        except:
            data = fetch(url)
            dump(data, cache_file)

    else:
        data = fetch(url)
        dump(data, cache_file)

    return data


def fetch_latest_water_level_data(use_cache=False):
    """Fetch latest levels from all 'measures'. Returns JSON object."""

    # URL for retrieving data
    url = "http://environment.data.gov.uk/flood-monitoring/id/measures?parameter=level&qualifier=Stage&qualifier=level"

    try:
        os.makedirs(sub_dir)
    except:
        pass
    cache_file = os.path.join(sub_dir, "waterlevel_data.json")

    # Attempt to load level data from file, otherwise fetch from EA API
    if use_cache:
        try:
            # Attempt to load from file
            data = load(cache_file)
        except:
            data = fetch(url)
            dump(data, cache_file)
    else:
        data = fetch(url)
        dump(data, cache_file)

    return data
