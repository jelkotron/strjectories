import time
import threading
import requests
from strwueue_utils import tle2latlonhgt
from skyfield.api import load
import json

DATAURL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active'

class Trajectories():
    def __init__(self):
        self.calc_thread = None
        self.fetch_thread = None
        self.calculating = False
        self.downloading = False
        self.tles = None
        self.num_tles = 0

    def calculate(self, tles=None, timeframe=None):
        self.calculating = True
        self.calc_thread = threading.Thread(target=self.calculations_run) 
        self.calc_thread.start()

    def calculations_run(self):
        while self.calculating:
            t0 = time
            print("Info: Trajectory calculation started at %s"%t0.strftime("%H : %M : %S"))
            num = 10
            for i in range(num):
                print("Info: Calculating %i of %i trajectories"%(i, num))
                time.sleep(0.1)
            t1 = time
            print("Info: Trajectory calculation finished at %s"%t1.strftime("%H : %M : %S"))
            self.calculating = False
                 
    def tle_download(self, url=None):
        self.downloading = True
        self.fetch_thread = threading.Thread(target=self.tle_fetch)
        self.fetch_thread.start()

    def tle_fetch(self, url=None):
        if url == None:
            url = DATAURL
        
        t0 = time.perf_counter()
        timestamp = time.gmtime()
        data = {
            'timestamp' : timestamp, 
            'satellites' : {}
        }
        print("Info: Querying new TLE data")
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
                

        self.tles = data
        self.downloading = False
        t1 = time.perf_counter()
        print("Info: TLE data aquired in %f"%(t1-t0))


    def tle_write(self, data, file):
        if file:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


    def greet(self):
        print(self.data)