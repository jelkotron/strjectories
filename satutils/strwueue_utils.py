from geopy import geocoders
from skyfield.api import EarthSatellite, wgs84

def location_query(input):
    gn = geocoders.Nominatim(user_agent="my_App")
    output = gn.geocode(input, exactly_one=False)
    return output

def tle2latlonhgt(line1, line2, id, timescale, time, to_degrees=True):
    satellite = EarthSatellite(line1, line2, id, timescale)
    geocentric = satellite.at(time)
    lat, lon = wgs84.latlon_of(geocentric)
    hgt = wgs84.height_of(geocentric)

    if to_degrees:
        lat = lat.degrees
        lon = lon.degrees

    return lat, lon, hgt.km