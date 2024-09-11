import time
import threading
import geopy.distance
from utils import lat_to_px, lon_to_px
from task import Task
from skyfield.api import load, EarthSatellite, wgs84
import random
import numpy as np
import queue


DATAURL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active'

resolution_x = 800
resolution_y = 600

class Satellite():
    def __init__(self, id, tle_1, tle_2, config=None, trajectories=None, load=None):
        if load:
            self.from_json(load)
            self.config = config
            self.trajectories = trajectories
        else:
            self.id = id
            self.tle_1 = tle_1
            self.tle_2 = tle_2
            self.trajectories = trajectories
            self.lat = None
            self.lon = None
            self.height = None
            self.distance_from = None
            self.distance_2D = None
            self.distance_3D = None
            self.in_range = False
            self.color = None
            self.pixel_x = 0
            self.pixel_y = 0
            self.render_obj = None
            self.engine = None
            self.priority = None 
            self.highlight = False
            self.render = True 
            

        if self.tle_1 and self.tle_2:
            blocks1 = self.tle_1.split(" ")
            blocks2 = self.tle_2.split(" ")
            self.classification = blocks1[1][-1]
            mean_motion = self.tle_2[-17:-6]
            # extra info: checksum = self.tle_2[:-1], num_revolutions = self.tle_2[-6:-2]
            try:
                self.mean_motion = float(mean_motion)
            except ValueError:
                self.mean_motion = None

        self.config = config
        if self.config.properties.lat and self.config.properties.lon:
            self.distance_from = [self.config.properties.lat, self.config.properties.lon]

    
    def update_target_location(self):
        self.distance_from =  [self.config.properties.lat, self.config.properties.lon]


    def update_coordinates(self):
        ts = load.timescale()
        satellite = EarthSatellite(self.tle_1, self.tle_2, self.id, ts)
        geocentric = satellite.at(ts.now())
        lat, lon = wgs84.latlon_of(geocentric)
        height = wgs84.height_of(geocentric)
        self.height = height.km
        self.lat = lat.degrees
        self.lon = lon.degrees
    

    def update_pixel_coordinates(self):
        if self.lon:
            self.pixel_x = lon_to_px(self.lon, resolution_x)
        if self.lat:
            self.pixel_y= lat_to_px(self.lat, resolution_x, resolution_y)
        

    def to_json(self):
        data = {
            "id": self.id,
            "tle_1": self.tle_1,
            "tle_2": self.tle_2,
            "mean_motion": self.mean_motion,
            "classification": self.classification,
            "lat": self.lat,
            "lon": self.lon,
            "height": self.height,
            "distance_from": self.distance_from,
            "radius": self.config.properties.radius,
            "distance_2D": self.distance_2D,
            "in_range": self.in_range,
            "distance_3D": self.distance_3D,
            "pixel_x": self.pixel_x,
            "pixel_y": self.pixel_y,
            "color": self.color,
            "highlight": self.highlight,
            "render": self.render,
            "render_obj": None
        }
        return data
    

    def from_json(self, data):
        self.id = data.get("id")
        self.tle_1 = data.get("tle_1")
        self.tle_2 = data.get("tle_2")
        self.classification = data.get("classification")
        self.mean_motion = data.get("mean_motion")
        self.lat = data.get("lat")
        self.lon = data.get("lon")
        self.height = data.get("height")
        self.distance_from = data.get("distance_from")
        self.distance_2D = data.get("distance_2D")
        self.radius = data.get("radius")
        self.in_range = data.get("in_range")
        self.distance_3D = data.get("distance_3D")
        self.pixel_x = data.get("pixel_x")
        self.pixel_y = data.get("pixel_y")
        self.color = data.get("color")
        self.highlight = data.get("highlight")
        self.render_obj = data.get("render_obj")
        self.render = data.get("render")


    def distance_2D_from(self, callback=None):
        lat, lon = self.config.properties.lat, self.config.properties.lon
        if lat and lon and self.lat and self.lon:
            self.distance_from = [lat, lon]
            # TODO: Dirty
            try:
                self.distance_2D = geopy.distance.geodesic((self.lat, self.lon), (lat, lon)).km
                if self.config.properties.radius:
                    previous = self.in_range
                    if self.config.properties.radius > self.distance_2D: 
                        self.in_range = True
                        if self.id not in self.trajectories.in_range:
                            self.trajectories.in_range.append(self.id)
                            self.trajectories.num_in_range += 1
                    else:
                        self.in_range = False
                        if self.id in self.trajectories.in_range:
                            self.trajectories.in_range.remove(self.id)
                            self.trajectories.num_in_range -= 1
                    if self.in_range != previous:
                        self.config.input_q.put(Task(type='IO', subtype='in_range_list')) 
                        if callback:
                            callback()
                            
            except ValueError:
                pass
            

    def in_range_get(self, callback=None):
        previous = self.in_range
        if self.distance_2D and self.config.properties.radius:
            if self.distance_2D <= self.config.properties.radius:
                self.in_range = True
            else:
                self.in_range = False
            if callback:
                if self.in_range != previous:
                    callback()

        return self.in_range


    def update(self):
        self.update_coordinates()
        self.distance_2D_from()
        self.update_pixel_coordinates()

        if self.render == False:
            if self.id in self.trajectories.in_range:
                self.trajectories.in_range.remove(self.id)
        else:
            if self.distance_2D and self.config.properties.radius:
                if self.distance_2D <= self.config.properties.radius:
                    self.in_range = True
                    if self.id not in self.trajectories.in_range:
                        self.trajectories.in_range.append(self.id)
                else:
                    self.in_range = False
                    if self.id in self.trajectories.in_range:
                        self.trajectories.in_range.remove(self.id)

        self.trajectories.render_queue.put(self)



class Trajectories():
    def __init__(self, config):
        self.config = config

        self.satellites = []
        self.sat_dict = {}
        self.num_tles = 0
        self.tle_file = None
        self.timestamp = None
        self.in_range = []
        self.num_in_range = 0
        self.classification_map = {
            "unclassified": 'u',
            "classified": 'c',
            "secret": 's',
        }
        self.saved = False
        self.tle_age = None
        self.sim_age = None

        self.render_queue = queue.Queue()
        self.calc_q_0 = queue.Queue()
        self.calc_q_1 = queue.Queue()

        self.running = False
        self.simulating = False
        self.time_0 = None

        self.time_age_check = time.perf_counter()
        self.last_saved = None

        self.running_0 = True
        self.thread_0 = threading.Thread(target=self.thread_0_run)
        self.thread_0.start()

        self.thread_1_current = 0
        self.running_1 = True
        self.thread_1 = threading.Thread(target=self.thread_1_run)
        self.thread_1.start()
        

    def simulating_set(self, value):
        if value == True:
            self.simulation_start()
        else:
            self.simulation_stop()
        

    def populate_calc_q_0(self):
        self.calc_q_0.queue.clear()
        for i in range(min(len(self.satellites), self.config.properties.t0_max)):
            self.calc_q_0.put(Task(type='CALCULATION', data=self.satellites[i]))


    def populate_calc_q_1(self):
        self.calc_q_1.queue.clear()
        num_sats = min(len(self.satellites), self.config.properties.t1_max)
        min_index = self.config.properties.t0_max
        for i in range(min_index, num_sats):
            self.calc_q_1.put(Task(type='CALCULATION', data=self.satellites[i]))


    def simulation_start(self, silent=False):
        self.simulating = True
        self.time_0 = time.time()
        
        if not silent:
            msg = "%s Simulation started"%self.config.time.strftime("%H:%M:%S")
            print(msg)
            self.config.log(msg)


    def simulation_stop(self, silent=False):
        self.time_0 = 0
        self.simulating = False

        if not silent:
            msg = "%s Simulation stopped"%self.config.time.strftime("%H:%M:%S")
            print(msg)
            self.config.log(msg)

        if self.config.properties.auto_save:
            self.config.data_save()

    def simulation_update(self):
        was_running = self.simulating 
        self.simulating = False
        self.sat_sort()
        self.populate_calc_q_0()
        self.populate_calc_q_1()
        self.simulating = was_running


    def thread_0_run(self):
        while True:

            dt = time.perf_counter() - self.time_age_check 
            if dt >= 30: # check age twice a minute
                self.calculate_sim_age()
                self.calculate_tle_age()
                self.time_age_check = time.perf_counter()

            if not self.simulating:
                time.sleep(0.1)

            else:
                if self.calc_q_0.empty():
                    self.sat_sort()
                    self.populate_calc_q_0()
                    # TODO: populate q_1 and make t_1 start from last
                else:
                    task = self.calc_q_0.get() 

                    sat = task.data
                    if sat.render:
                        sat.update()

                    if self.config.properties.auto_render:
                        self.render_queue.put(sat)
                
                    self.calc_q_0.task_done()


    def thread_1_run(self):
        while True:
            if not self.simulating:
                time.sleep(0.1)

            else:
                if self.calc_q_1.empty():
                    self.sat_sort()
                    self.populate_calc_q_1()
                else:
                    task = self.calc_q_1.get()
                    if task.type == 'CALCULATION':
                        sat = task.data
                        if sat.render:
                            sat.update()

                        if self.config.properties.auto_render:
                            self.render_queue.put(sat)
                    
                    self.calc_q_1.task_done()

    
    def update_filter(self, mode='AND'):
        classification = self.config.properties.classification
        filter = self.config.properties.filter
        c_map = { 
            'Unclassified': 'U', 
            'Classified': 'C', 
            'Secret': 'S'
            }
        
        for i in range(len(self.satellites)):
            sat = self.satellites[i]
            render = 1 # True

            if len(filter) > 0:
                if mode == 'AND':
                    for f in self.config.properties.filter:
                        render *= (f.lower() in sat.id.lower())
                elif mode == 'OR':
                    for f in self.config.properties.filter:
                        render += (f in sat.id)

            if classification != 'All':
                render *= (sat.classification == c_map[classification])

            # set state
            if render == 0 or i > self.config.properties.t1_max:
                sat.render = False
            else:
                sat.render = True
    

    def calculate_tle_age(self):
        if self.timestamp:
            then = np.array([i for i in self.timestamp])
            now = np.array([i for i in time.gmtime()])
            
            then = '-'.join(str(i).zfill(2) for i in then[:3]) + ' ' + ':'.join(str(i).zfill(2) for i in then[3:5])
            now = '-'.join(str(i).zfill(2) for i in now[:3]) + ' ' + ':'.join(str(i).zfill(2) for i in now[3:5])

            then = np.datetime64(then)
            now = np.datetime64(now)
            delta = np.timedelta64((now - then), 'h')
            self.tle_age = delta

            self.config.input_q.put(Task(type='INFO_UPDATE', callback=None, subtype='tle_age'))

            if self.config.properties.auto_download:
                if delta.astype(int) >= self.config.properties.auto_download_interval:    
                    self.tle_request()        
                    
            return delta


    def calculate_sim_age(self):
        if self.last_saved:
            then = np.array([i for i in self.last_saved])
            now = np.array([i for i in time.gmtime()])
            
            then = '-'.join(str(i).zfill(2) for i in then[:3]) + ' ' + ':'.join(str(i).zfill(2) for i in then[3:6])
            now = '-'.join(str(i).zfill(2) for i in now[:3]) + ' ' + ':'.join(str(i).zfill(2) for i in now[3:6])
            
            then = np.datetime64(then)
            now = np.datetime64(now)
            delta = np.timedelta64((now - then), 'm')
            self.sim_age = delta

            self.config.input_q.put(Task(type='INFO_UPDATE', callback=None, subtype='sim_age'))

            if self.config.properties.auto_save:
                if delta.astype(int) >= self.config.properties.auto_save_interval:            
                    self.config.input_q.put(Task(type='FILE_WRITE', callback=None, subtype='DATA'))


            return delta
            

    def in_range_update(self):
        for i in range(len(self.satellites)):
            sat = self.satellites[i]
            if sat.render == False:
                if sat.id in self.in_range:
                    self.in_range.remove(sat.id)
            else:
                if sat.distance_2D and self.config.properties.radius:
                    if sat.distance_2D <= self.config.properties.radius:
                        sat.in_range = True
                        if sat.id not in self.in_range:
                            self.in_range.append(sat.id)
                    else:
                        sat.in_range = False
                        if sat.id in self.in_range:
                            self.in_range.remove(sat.id)


    def reset_render_queue(self, repopulate=True):
        self.render_queue = queue.Queue()
        if not repopulate:
            return
        self.in_range_update()
        for obj in self.satellites:
            self.render_queue.put(obj)


    def update_once(self, update_coords=True, update_dist=True, callback=None):
        was_simulating = self.simulating
        self.simulating = False

        self.sat_sort()
        self.update_filter()
        self.reset_render_queue(repopulate=False)

        for i in range(len(self.satellites)):
            obj = self.satellites[i]
            if update_coords:
                obj.update_coordinates()
                obj.update_pixel_coordinates()
            if update_dist:
                obj.distance_2D_from()
                
            self.render_queue.put(obj)

        self.config.input_q.put(Task(type='IO', subtype='in_range_list'))


        if callback:
            callback()

        self.simulating = was_simulating


    def update_target_location(self):
        for i in range(len(self.satellites)):
            sat = self.satellites[i]
            if sat.lat and sat.lon:
                sat.update_target_location()
                sat.distance_2D_from()
        self.in_range_update()
        self.simulation_update()
        self.saved_set(False)


    def tle_request(self, new_file=False):
        self.timestamp = time.gmtime()
        if new_file == False:
            self.config.data_refresh()
        else:
            self.saved_set(False)
            self.config.data_new()


    def tle_update(self, data, mode=None):
        was_running = self.simulating 
        self.simulating = False
        
        if mode == 'QUERY':
            self.timestamp = time.gmtime()
            text = data.text.split("\n")
            objects = self.tle_parse(data.text)

            for id, tle in objects.items():
                if id not in self.sat_dict:
                    if mode == 'QUERY':
                        sat = Satellite(id, tle[0], tle[1], self.config, self)

                    self.satellites.append(sat)
                    self.sat_dict[id] = sat
                    self.num_tles += 1
                else:
                    # TODO: if these are not pointers, there will be problems
                    self.sat_dict[id].tle_1 = tle[0]
                    self.sat_dict[id].tle_2 = tle[1]
        
            if self.config.properties.auto_save == True:
                self.config.input_q.put(Task(type='FILE_WRITE', callback=None, subttype='DATA'))

            self.simulating = was_running
            msg = "%s TLE Data updated"%self.config.time.strftime("%H:%M:%S")
            print(msg)
            self.config.log(msg)
            self.saved_set(False)
        
        elif mode == 'DATA':
            self.set(data)
            self.saved_set(True)

      
    def tle_parse(self, text):
        text = text.split('\n')
        objects = {}
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
                objects[id] = [tle_1, tle_2]

        return(objects)
    

    def to_json(self):
        self.sat_sort()
        self.last_saved = time.gmtime()
        self.calculate_tle_age()
        self.calculate_sim_age()
        data = {
            "timestamp": self.timestamp,
            "last_saved": self.last_saved,
            "num_tles": self.num_tles,
            "satellites": [i.to_json() for i in self.satellites],
            "sort_by": self.config.properties.sort_by,
            # "tle_age": str(self.tle_age),
            # "sim_age": str(self.sim_age)

        }

        return data

    def get(self, value):
        data = {
            "timestamp": self.timestamp,
            "last_saved": self.last_saved,
            "num_tles": self.num_tles,
            "satellites": [i.to_json() for i in self.satellites],
            "sort_by": self.config.properties.sort_by,
            "tle_age": str(self.tle_age),
            "sim_age": str(self.sim_age),
            "saved": self.saved,
        }
        return(data[value])


    def saved_set(self, value=True):
        self.saved = value
        if value == True:
            self.last_saved = time.gmtime()
        self.config.input_q.put(Task(type='INFO_UPDATE', subtype='tle_file'))
        self.config.input_q.put(Task(type='INFO_UPDATE', subtype='sim_age'))
        

    def read(self, file, set_values=True):
        self.tle_file = file
        if file:

            for i in range(len(self.satellites)):
                sat = self.satellites[i]
                self.render_queue.put(sat)

        self.saved_set(True)

        msg = "%s Data loaded: %s"%(self.config.time.strftime("%H:%M:%S"), file)
        print(msg)
        self.config.log(msg)
            

    def set(self, data=None):
        if data:
            self.satellites = []
            self.sat_dict = {}

            satellites = data.get("satellites")

            if satellites:
                for s in satellites:
                    sat = Satellite(None, None, None, self.config, self, s)
                    self.satellites.append(sat)
                    self.sat_dict[s["id"]] = sat

            self.num_tles = data.get('num_tles') if data.get('num_tles') else 0
            self.timestamp = data.get('timestamp')
            self.last_saved = data.get('last_saved')
            self.calculate_sim_age()
            self.calculate_tle_age()
            self.tle_file = data.get('tle_file')

            for i in range(len(self.satellites)):
                sat = self.satellites[i]
                self.render_queue.put(sat)

            self.sat_sort()
            
            msg = "%s TLE Data initialized"%(self.config.time.strftime("%H:%M:%S"))
            print(msg)
            self.config.log(msg)

    
    def qsort(self, a, low, high):
        if high <= low:
            return
        # select the pivot randomly
        pivot_index = random.randint(low, high)
        pivot = a[pivot_index]
        
        # place it at the end
        # and proceed as usual
        a[pivot_index], a[high] = a[high], a[pivot_index]
        
        # partition the input
        split_index = low
        for i in range(low, high):
            if self.config.properties.sort_by == None or self.config.properties.sort_by == 'PROXIMITY':
                if a[i].distance_2D <= a[high].distance_2D:
                    a[split_index], a[i] = a[i], a[split_index]
                    split_index = split_index + 1

            elif self.config.properties.sort_by == 'SPEED':
                if a[i].mean_motion >= a[high].mean_motion:
                    a[split_index], a[i] = a[i], a[split_index]
                    split_index = split_index + 1
        
        # place the pivot between the lower and greater elements
        a[split_index], a[high] = a[high], a[split_index]
        
        # sort the left and right parts
        self.qsort(a, low, split_index - 1)
        self.qsort(a, split_index + 1, high)
        

    def sat_sort(self):
        if self.config.properties.sort_by == 'PROXIMITY':
            measured = []
            unmeasured = []
            for i in range(len(self.satellites)):
                sat = self.satellites[i]
                if sat.distance_2D == None:
                    unmeasured.append(sat)
                else:
                    measured.append(sat)
                    
            random.shuffle(measured)

            self.qsort(measured, 0, len(measured)-1)
            self.satellites = measured + unmeasured


        elif self.config.properties.sort_by == 'SPEED':
            measured = self.satellites 
            self.qsort(measured, 0, len(measured)-1)
            self.satellites = measured

        self.saved_set(False)
    
            
    def clear(self):
        self.satellites = []
        self.num_tles = 0
        self.tle_file = None
        self.timestamp = None
        self.tle_file = None