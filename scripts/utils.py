from geopy import geocoders
from skyfield.api import EarthSatellite, wgs84
import timezonefinder
import math
import serial
import time

r_earth = 6378.137

def serial_out(serialport, baudrate=600):
    try:
        ser = serial.Serial(serialport, baudrate, timeout=1)
        print("%s Serial port opened: %s"%(time.strftime("%H:%M:%S"), serialport))
        return ser
    except serial.SerialException:
        print("%s Error: Serial port not found: %s"%(time.strftime("%H:%M:%S"), serialport))
        return None


def location_query(input):
    gn = geocoders.Nominatim(user_agent="strwüü")
    output = gn.geocode(input, exactly_one=False)
    return output

def timezone_query(lat, lon):
    obj = timezonefinder.TimezoneFinder()
    tz = obj.timezone_at(lng=lon, lat=lat)
    return tz
    

def tle2latlonhgt(line1, line2, id, timescale, time, to_degrees=True):
    satellite = EarthSatellite(line1, line2, id, timescale)
    geocentric = satellite.at(time)
    lat, lon = wgs84.latlon_of(geocentric)
    hgt = wgs84.height_of(geocentric)

    if to_degrees:
        lat = lat.degrees
        lon = lon.degrees

    return lat, lon, hgt.km

def lat_plus_m(lat, m):
    new_lat  = lat  + (m / r_earth) * (180 / math.pi)
    return new_lat

def lon_plus_m(lat, lon, m):
    new_lon = lon + (m / r_earth) * (180 / math.pi) / math.cos(lat * math.pi/180)
    return new_lon


def lat_to_m(lat, unit='km'):
    d_km = math.pi/180 * r_earth / lat
    if unit == 'm':
        return d_km * 1000
    return d_km

def lon_to_m(lat, lon, units='km'):
    km_per_degree = math.pi/180 * r_earth * math.cos(lat*math.pi/180)
    d_km = lon * km_per_degree
    if units == 'm':
        return d_km * 1000
    return d_km

def lat_to_px(lat, pixels_x, pixels_y):
    mercN = math.log(math.tan((math.pi / 4) + (math.radians(lat) / 2)))
    y = (pixels_y / 2) - (pixels_x * mercN / (2 * math.pi))
    return y

def lon_to_px(lon, pixels_x):
    return (lon+180) * (pixels_x / 360)


def measure(lat0, lon0, lat1, lon1):
    d_y = abs(lat_to_m(lat0) - lat_to_m(lat1))
    d_x = abs(lon_to_m(lat0, lon0) - lon_to_m(lat1, lon1))
    dist = math.sqrt(d_y**2 + d_x**2)
    return dist
    
    