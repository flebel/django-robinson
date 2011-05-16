from robinson.exceptions import UnknownLocationError
from gmapi import maps


def dms_to_decimal((degrees, minutes, seconds)):
    """
    Converts a value from a (degree, minute, second) tuple to a float.
    http://code.google.com/p/geolocator/source/browse/trunk/geolocator/gislib.py
    """
    return abs(degrees) + (minutes / 60.0) + (seconds / 3600.0)

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

def get_latitude_ref_multiplier(imgMetadata):
    """
    Returns the latitude multiplier according to the
    Exif.GPSInfo.GPSLatitudeRef EXIF tag contained in the imgMetadata dict.
    """
    if imgMetadata['Exif.GPSInfo.GPSLatitudeRef'].value.lower() == 's':
        return -1
    return 1

def get_latitude_tuple(imgMetadata):
    """
    Returns the tuple containing the degrees, minutes and seconds of the
    latitude coordinate as float values.
    """
    return (imgMetadata['Exif.GPSInfo.GPSLatitude'].value[0].to_float(), imgMetadata['Exif.GPSInfo.GPSLatitude'].value[1].to_float(), imgMetadata['Exif.GPSInfo.GPSLatitude'].value[2].to_float())

def get_longitude_ref_multiplier(imgMetadata):
    """
    Returns the longitude multiplier according to the
    Exif.GPSInfo.GPSLongitudeRef EXIF tag contained in the imgMetadata dict.
    """
    if imgMetadata['Exif.GPSInfo.GPSLongitudeRef'].value.lower() == 'w':
        return -1
    return 1

def get_longitude_tuple(imgMetadata):
    """
    Returns the tuple containing the degrees, minutes and seconds of the
    longitude coordinate as float values.
    """
    return (imgMetadata['Exif.GPSInfo.GPSLongitude'].value[0].to_float(), imgMetadata['Exif.GPSInfo.GPSLongitude'].value[1].to_float(), imgMetadata['Exif.GPSInfo.GPSLongitude'].value[2].to_float())

