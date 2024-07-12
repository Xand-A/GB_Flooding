"""This module provides a model for a flood warning """

from .datafetcher import fetch
from shapely.geometry import Polygon, MultiPolygon


class FloodWarning:
    """This class represents a EA flood warning"""

    def __init__(
        self,
        message,
        description,
        flood_url,
        area_name,
        area_id,
        river_sea,
        severity,
        county,
        time_raised,
        time_message_changed,
        time_severity_changed,
    ):

        self.message = message
        self.description = description
        self.url = flood_url
        self.area_name = area_name
        self.area_id = area_id
        self.river_sea = river_sea
        self.severity = severity
        self.county = county
        self.time_raised = time_raised
        self.time_message_changed = time_message_changed
        self.time_severity_changed = time_severity_changed

    def __repr__(self):

        d = "Flood description:            {}\n".format(self.description)
        d += "      message:                {}\n".format(self.message)
        d += "      id:                     {}\n".format(self.url)
        d += "      area name:              {}\n".format(self.area_name)
        d += "      area id:                {}\n".format(self.area_id)
        d += "      river/sea:              {}\n".format(self.river_sea)
        d += "      severity:               {}\n".format(self.severity)
        d += "      county:                 {}\n".format(self.county)
        d += "      time raised:            {}\n".format(self.time_raised)
        d += "      message change at:      {}\n".format(self.time_message_changed)
        d += "      severity change at:     {}\n".format(self.time_severity_changed)

        return d
