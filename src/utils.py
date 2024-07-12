""" This contains utility functions required by stationdata"""

def sorted_by_key(x, i, reverse=False):
    """For a list of lists/tuples, return list sorted by the ith component
    E.g.
    
    Sorted on first entry of tuple:
    > sorted_by_key([(1,2), (5,1)] , 0)
    >>> [(1,2), (5,1)]

    Sorted on second entry of tuple:
    > sorted_by_key([(1,2), (5,1)] , 1)
    >>> [(5,1), (1,2)]

    """

    # Sort by distance
    def key(element):
        return element[i]
    
    return sorted(x, key=key, reverse=reverse)