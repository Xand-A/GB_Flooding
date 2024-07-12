"""This module provides a model for a river-level monitoring station, 
and tools for manipulating station data
"""


class MonitoringStation:
    """This class represents a river-level monitoring station"""

    def __init__(
        self, station_id, measure_id, label, coord, typical_range, river, town
    ):

        self.station_id = station_id
        self.measure_id = measure_id

        # handle the special case where the API returns
        # '[label, label]' rather than 'label'
        self.name = label
        if isinstance(label, list):
            self.name = label[0]

        self.coord = coord
        self.typical_range = typical_range
        self.river = river
        self.town = town

        self.latest_level = None

    def __repr__(self):
        d = "Station name:          {}\n".format(self.name)
        d += "        id:            {}\n".format(self.station_id)
        d += "        measure id:    {}\n".format(self.measure_id)
        d += "        coordinate:    {}\n".format(self.coord)
        d += "        town:          {}\n".format(self.town)
        d += "        river:         {}\n".format(self.river)
        d += "        typical range: {}\n".format(self.typical_range)
        d += "        latest level:  {}".format(self.latest_level)
        return d

    def typical_range_consistent(self):
        """Check the typical range for consistency.
        Returns True if consistent, and returns False if
        inconsistent or unavailable.
        """

        consistent = False
        if self.typical_range is not None:
            if self.typical_range[0] < self.typical_range[1]:
                consistent = True

        return consistent

    def relative_water_level(self):
        """Return latest water level as a fraction of the typical
        range. Returns None if data is inconsistent or unavailable.
        """

        # check consistency
        consistent = self.typical_range_consistent()

        # compute relative level (if consistent)
        if consistent and self.latest_level is not None:
            typ_range = self.typical_range
            return (self.latest_level - typ_range[0]) / (typ_range[1] - typ_range[0])
        else:
            return None


def inconsistent_typical_range_stations(stations):
    """Returns a list of stations with inconsistent data using
    the typical_range_consistent method
    """

    inconsistent_stations = [
        station for station in stations if not station.typical_range_consistent()
    ]

    return inconsistent_stations
