#!/home/schnollie/.venvs/strwueue/bin/python
import json
import time 
import requests
from skyfield.api import Distance, load, wgs84, EarthSatellite
from skyfield.positionlib import Geocentric


def tle2latlonhgt(line1, line2, id, timescale, time, to_degrees=True):
    satellite = EarthSatellite(line1, line2, id, timescale)
    geocentric = satellite.at(time)
    lat, lon = wgs84.latlon_of(geocentric)
    hgt = wgs84.height_of(geocentric)

    if to_degrees:
        lat = lat.degrees
        lon = lon.degrees

    return lat, lon, hgt.km


class Sat(object):
    def __init__(self, id, tle):
        self.id = id
        self.tle = tle
        self.keyframes = []
        

    def get_keyframes(self, t0, frame_time, num_frames):
        ts = load.timescale()
        utc_time = ts.now().utc
        years = utc_time[0]
        months = utc_time[1]
        days = utc_time[2]
        hours = utc_time[3]
        minutes = utc_time[4]
        seconds = utc_time[5] 
        
        l1 = self.tle.split('\n')[0]
        l2 = self.tle.split('\n')[1]
        
        steps = ts.utc(years, months, days, hours, minutes, range(num_frames))
        
        for time in steps:
            kf = tle2latlonhgt(l1, l2, self.id, ts, time)
            self.keyframes.append({time: kf})





class SatCat(object):
    def __init__(self, file):
        self.file = file
        self.objects = []


    def fetch(self, url):
        t0 = time.perf_counter()
        timestamp = time.gmtime()
        data = {
            'timestamp' : timestamp, 
            'satellites' : {}
        }
        r = requests.get(url)
        text = r.text.split("\n")

        for i in range(len(text)-2):
            line = text[i]
            id = None
            tle_1 = None
            tle_2 = None

            if not line.startswith("1") and not line.startswith("2"):
                id = line.strip()
                tle_1 = text[i+1].strip()
                tle_2 = text[i+2].strip()

            if id and tle_1 and tle_2:
                ts = load.timescale()
                lat, lon, hgt = tle2latlonhgt(tle_1, tle_2, id, ts, ts.now())

                data['satellites'][id] = {
                    'tle': '\n'.join([tle_1, tle_2]),
                    'lat': lat,
                    'lon': lon,
                    'height': hgt
                    }
                

        self.write(data, self.file)

        t1 = time.perf_counter()
        print("Fetch: Finished in %f seconds"%(t1-t0))


    def write(self, data, file):
        if file:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)



    def read(self, file=None):
        t0 = time.perf_counter()
        if not file:
            file = self.file

        if file:

            ts = load.timescale() # TODO: unify!
            d = None
            with open(file, 'r') as f:
                d = json.load(f)
                
            
        t1 = time.perf_counter()
        perf = t1 - t0
        print("Read: Finished in %f seconds."%perf)
        
        return d

    def update(self, file):
        pass



    