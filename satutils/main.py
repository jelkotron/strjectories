#!/home/schnollie/.venvs/strwueue/bin/python
from map import live_plotter, map_plotter
import requests
import numpy
import json
import time 
import os

from skyfield.api import Distance, load, wgs84, EarthSatellite
from skyfield.positionlib import Geocentric

from satcat import SatCat, Sat

# def tle2latlonhgt(line1, line2, id, timescale, to_degrees=True):
#     satellite = EarthSatellite(line1, line2, id, timescale)
#     geocentric = satellite.at(timescale.now())
#     lat, lon = wgs84.latlon_of(geocentric)
#     hgt = wgs84.height_of(geocentric)

#     if to_degrees:
#         lat = lat.degrees
#         lon = lon.degrees

#     return lat, lon, hgt

# def fetch_satellites(url, file='/tmp/satlist.json'):
#     t0 = time.perf_counter()
#     timestamp = time.gmtime()
#     data = {
#         'timestamp' : timestamp, 
#         'satellites' : {}
#     }
#     r = requests.get(url)
#     text = r.text.split("\n")

#     for i in range(len(text)-2):
#         line = text[i]
#         id = None
#         tle_1 = None
#         tle_2 = None

#         if not line.startswith("1") and not line.startswith("2"):
#             id = line.strip()
#             tle_1 = text[i+1].strip()
#             tle_2 = text[i+2].strip()

#         if id and tle_1 and tle_2:
#             ts = load.timescale()
#             lat, lon, hgt = tle2latlonhgt(tle_1, tle_2, id, ts)

#             data['satellites'][id] = {
#                 'tle': '\n'.join([tle_1, tle_2]),
#                 'lat': lat,
#                 'lon': lon,
#                 'height': hgt,
#                 }
            

#     with open(file, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

#     t1 = time.perf_counter()
#     print("Fetch: Finished in %f seconds"%(t1-t0))



# def read_satellites(file):
#     t0 = time.perf_counter()
#     ts = load.timescale() # TODO: unify!
#     t = ts.utc(2014, 1, 23, 11, 18, 7)
#     with open(file, 'r') as f:
#         d = json.load(f)
        
#         for key, value in d["satellites"].items():
#             tle = value['tle'].split('\n')
           
#             print('id:', key)
#             print('Latitude:', value["lat"])
#             print('Longitude:', value["lon"])
    
#     t1 = time.perf_counter()
#     perf = t1 - t0
#     print("Read: Finished in %f seconds."%perf)


url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active'
file = '/tmp/satlist.json'

catalog = SatCat(file)
d = catalog.read()
num = 0
MAX_SATELLITES = 100000

t_perf0 = time.perf_counter()

for id, info in d["satellites"].items():
    if num < MAX_SATELLITES:
        sat = Sat(id, info['tle'])
        sat.get_keyframes(None, 1, 60)
        for k in sat.keyframes:
            print(k)
        num += 1

t_perf1 = time.perf_counter()
d_t_perf = t_perf1 - t_perf0
print("Animation: Finished in %f seconds"%d_t_perf)
