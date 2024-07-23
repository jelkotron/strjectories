#!/home/schnollie/.venvs/strwueue/bin/python
import json
import time 
import requests
from skyfield.api import Distance, load, wgs84, EarthSatellite, utc
from skyfield.positionlib import Geocentric
from datetime import timedelta, datetime, timezone

MAX_SATELLITES = 1
TIMEFORMAT = '%Y-%m-%d %H:%M:%S'

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
    def __init__(self, id, tle, timescale, t0):
        self.id = id
        self.tle = tle.split('\n')
        self.keyframes = []
        self.timescale = timescale
        self.t0 = t0
        self.lat, self.lon, self.hgt = 0, 0, 0

    def create_keyframes(self, num_frames, frame_time):
        years, months, days, hours, minutes, seconds = self.t0
        steps = self.timescale.utc(years, months, days, hours, minutes, range(0, num_frames*frame_time, frame_time))

        for i in range(len(steps)):
            time = steps[i]
            kf = tle2latlonhgt(self.tle[0], self.tle[1], self.id, self.timescale, time)
            self.keyframes.append([time.utc_strftime(TIMEFORMAT), kf])

        self.lat = self.keyframes[0][1][0]
        self.lon = self.keyframes[0][1][1]
        self.hgt = self.keyframes[0][1][2]

    def interpolate_keyframes(self, num_substeps):
        substeps = []
        for i in range(len(self.keyframes)):
            if i > 0:
                for j in range(num_substeps):
                    kf = self.keyframes[i]
                    t = datetime.strptime(kf[0], TIMEFORMAT)

                    kf_previous = self.keyframes[i-1]
                    t_previous = datetime.strptime(kf_previous[0], TIMEFORMAT)
  
                    secs = (t - t_previous) / (num_substeps+1) * (j+1)
                    d_time = t_previous + timedelta(seconds = secs.total_seconds())

                    d_lat = kf_previous[1][0] + (kf[1][0] - kf_previous[1][0]) / num_substeps * j
                    d_lon = kf_previous[1][1] + (kf[1][1] - kf_previous[1][1]) / num_substeps * j
                    d_hgt = kf_previous[1][2] + (kf[1][2] - kf_previous[1][2]) / num_substeps * j
                    
                    substeps.append(
                        [d_time.strftime(TIMEFORMAT), (d_lat, d_lon, d_hgt)]
                    )

            substeps.append(self.keyframes[i])
                    
        self.keyframes = substeps

    def update_position(self):
        t_now = self.timescale.now().utc
        num_rm = 0
        if len(self.keyframes) > 0:
            t_key = datetime.strptime(self.keyframes[0][0], TIMEFORMAT).replace(tzinfo=utc)
            t_key = self.timescale.utc(t_key).utc
            while t_key < t_now:
                try:
                    self.keyframes.pop(0)
                    num_rm += 1
                except IndexError:
                    pass
        
        if num_rm > 0:
            print("Info: Removed %i obsolete keyframes."%num_rm)

        if len(self.keyframes) > 0:
            key = self.keyframes.pop(0)
            self.lat, self.lon, self.hgt = key[1]

        # for i in range(len(self.keyframes)):
        #     key = self.keyframes[i]
        #     t_key = datetime.strptime(key[0], TIMEFORMAT).replace(tzinfo=utc)
        #     t_key = self.timescale.utc(t_key).utc
            
        #     if t_key < t_now:

            # print(t_key)
            # print(type(t_key))
            # print("################################")
            # print("-->", t_now)
            # print(type(t_now))
            # print("################################")

            

class SatCat(object):
    def __init__(self, file):
        self.file = file
        self.num_objects = 0
        self.objects = []
        self.timescale = load.timescale()
        self.t0 = self.timescale.now().utc

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
            ts = load.timescale()
            data = None
            with open(file, 'r') as f:
                data = json.load(f)

        for id, info in data["satellites"].items():
            sat = Sat(id, info['tle'], self.timescale, self.t0)
            self.objects.append(sat) # TODO: Evaluate data type
            self.num_objects += 1

        t1 = time.perf_counter()
        perf = t1 - t0
        print("Read: Finished in %f seconds."%perf)
        return data


    def create_keyframes(self, num_frames, frame_time):
        for i in range(MAX_SATELLITES):
            if i < len(self.objects):
                sat = self.objects[i]
                sat.create_keyframes(num_frames, frame_time)
                
    
    def interpolate_keyframes(self,num_substeps):
        for sat in self.objects:
            sat.interpolate_keyframes(num_substeps)


    def print_keyframes(self):
        for sat in self.objects:
            for k in sat.keyframes:
                print(k)


    def update(self, file):
        pass



    