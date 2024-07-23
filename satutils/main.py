#!/home/schnollie/.venvs/strwueue/bin/python
import time 
import os
from satcat import SatCat, Sat

# from map import live_plotter, map_plotter
# import requests
# import numpy
# import json

# from skyfield.api import Distance, load, wgs84, EarthSatellite
# from skyfield.positionlib import Geocentric
SATCATPATH = '/tmp/satlist.json'
DATAURL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active'
MAX_SATELLITES = 1

MINUTE = 60
HOUR = 3600
DAY = 86400


def main(file=None, url=None):
    if not url:
        url = DATAURL
     
    if not file:
        file = SATCATPATH
        if not os.path.isfile(file):
            catalog = SatCat(file)
            print("Info: Retrieving Data from %s"%url)
            catalog.fetch(url)
            print("Info: Download successful")
            
            # TODO: Execption Handling; update file
        else:
            print("Info: Reading Data from %s"%file)

    catalog = SatCat(file)
    data = catalog.read()
    catalog.create_keyframes(10, HOUR)
    catalog.interpolate_keyframes(10)
    
    for i in range(len(catalog.objects)):
        obj = catalog.objects[i]
        obj.update_position()
    
 
            


main()