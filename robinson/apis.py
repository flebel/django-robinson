from django.utils.translation import ugettext_lazy as _
from robinson.exceptions import UnknownLocationError
from gmapi import maps


def elevation(latitude, longitude):
    """
    Returns the results of the call to Google's elevation API.
    """
    elevation = maps.Elevation()
    request = {'locations': '%f,%f' % (latitude, longitude)}
    results, status = elevation.elevation(request)
    if results:
        # We are only interested in the actual elevation
        return results[0]['elevation']
    else:
        raise UnknownLocationError(_('The location could not be found by the elevation API.'))

def geocode(location):
    """
    Returns the results of the call to Google's geocoding API.
    """
    geocoder = maps.Geocoder()
    request = {'address': location}
    results, status = geocoder.geocode(request)
    if results:
        # We are only interested in the first result returned
        return results[0]
    else:
        raise UnknownLocationError(_('The location could not be found by the geocoding API.'))

