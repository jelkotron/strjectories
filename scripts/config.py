import os
import time
from trajectories import Trajectories
from task import Task
import json 
import queue
import threading
import requests
import serial
import timezonefinder
from geopy import geocoders
import schedule
import gpiod


DATAURL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active'


class ConfigIo():
    def __init__(self):
        self.time = time
        self.input_q = queue.Queue()
        self.ui_q = queue.Queue()
        
        self.running = False
        self.sleeping = False
        self.io_thread = None

        self.serial = None
        self.serial_data_previous = None

        self.properties = ConfigData(self.input_q, self.ui_q)
        self.trajectories = Trajectories(self)
        self.schedule = schedule

        self.session_load()

        self.start()


    def start(self):
        self.running = True
        self.io_thread = threading.Thread(target=self.run)
        self.io_thread.start()

   
    def stop(self):
        self.running = False
        self.io_thread = None


    def run(self):
        while self.running:
            if self.input_q.empty():
                self.schedule.run_pending()
                time.sleep(0.1)
            else:
                task = self.input_q.get()
                self.process(task)
                self.input_q.task_done()
          

    def sleep_schedule(self, sleep_time, wake_time, clear=False):
        self.schedule.clear()
        if clear == False:
            if sleep_time == None:
                sleep_time = self.properties.sleep_time
            if wake_time == None:
                wake_time = self.properties.wake_time
            self.schedule.every().day.at(sleep_time).do(self.sleep)
            self.schedule.every().day.at(wake_time).do(self.wake)


    def toggle_sleep(self, event=None):
        if self.sleeping:
            self.wake()
        else:
            self.sleep()
        self.toggle_line_value("/dev/gpiochip0", 18)

    def sleep(self):
        self.sleeping = True
        self.input_q.put(Task(type='IO', subtype='sleep'))


    def wake(self):
        self.sleeping = False
        self.input_q.put(Task(type='IO', subtype='sleep'))


    def process(self, task):
        #### Simulation / Rendering ####
        if task.type == 'SIMULATION':
            if task.subtype == 'sort_by':
                if self.trajectories:
                    self.trajectories.simulation_update()
               
            if task.subtype == 'selection' or task.subtype == 'radius':
                self.trajectories.update_target_location()
               
            if task.subtype in ['filter','threads', 'classification']:
                self.trajectories.update_filter()
               
            if task.subtype == 'timezone':
                os.environ['TZ'] = self.properties.timezone
                self.time.tzset()

            self.ui_q.put(task)


        if task.type == 'IO':
            self.io_update(task)
            self.ui_q.put(task)
            # if task.subtype == 'in_range_list':
            #     self.ui_q.put(Task(type='SIMULATION', subtype='in_range_list'))



        #### Automation ####
        if task.type == 'AUTOMATION_UPDATE':
            if task.subtype == 'auto_sleep':
                self.sleep_schedule(None, None, clear = not self.properties.auto_sleep)


        #### Query ####
        if task.type == 'DATA_QUERY':
            self.url_request(task.kwargs.get('url'), task.callback)

        if task.type == 'LOCATION_QUERY':
            self.location_request(task.data)

        if task.type == 'TIMEZONE_QUERY':
            self.timezone_request(task.data, task.callback)

        #### File ####
        if task.type == 'FILE_READ':
            self.file_read(task.callback, **task.kwargs)

        if task.type == 'FILE_WRITE':
            self.file_write(task.callback, **task.kwargs)
        
        #### Serial ####
        if task.type == 'SERIAL_OPEN':
            self.serial_open()

        if task.type == 'SERIAL_CLOSE':
            self.serial_close()
        
        if task.type == 'SERIAL_WRITE':
            data = ""
            if self.properties.serial_value == "In Range Count":
                data = str(len(self.trajectories.in_range))
            elif self.properties.serial_value == "No Satellites in Range":
                data = str(len(self.trajectories.in_range)==0)
            elif self.properties.serial_value == "Satellites in Range":
                data = str(len(self.trajectories.in_range)!=0)
                
            self.serial_write(data)
        
       
           
        
        #### Info ####
        #TODO: evaluate elegance of this
        if task.type == 'INFO_UPDATE':
            self.ui_q.put(Task(type=task.type, subtype=task.subtype))

        #### Log ####
        if task.type == 'LOG_WRITE':
            self.log_write(task.kwargs.get('message'))

        return True


    ######## Simulation ########
    def simulation_start(self):
        if self.trajectories:
            self.trajectories.simulation_start()
            self.ui_q.put(Task(type='SIMULATION', subtype='toggle', data=1))

    def simulation_stop(self):
        if self.trajectories:
            self.trajectories.simulation_stop()
            self.ui_q.put(Task(type='SIMULATION', subtype='toggle', data=0))
            

    ######## File ########
    def file_read(self, callback=None, **kwargs):
        subtype = kwargs.get('subtype')
        path = kwargs.get('path')
        result = None
        if subtype and path:
            if os.path.isfile(path):
                if subtype == 'SESSION':
                    f = open(path)
                    config, tles = None, None
                
                    lines = f.readlines()
                    if len(lines) >= 1:
                        config = lines[0].strip()
                        if len(lines) == 2:
                            tles = lines[1].strip()

                        if config:
                            config = config if os.path.isfile(config) else None
                        if tles:
                            tles = tles if os.path.isfile(tles) else None
                    
                    result = {"sessiondata_file": path}

                    if config:
                        result["config"] = config
                        self.config_file = config
                    if tles:
                        result["tles"] = tles
                        self.tles = tles
                    f.close()
                
    
                if subtype == 'DATA' or subtype == 'CONFIG':
                    try:
                        f = open(path)
                        data = json.load(f)
                        init = kwargs.get("init") if kwargs.get("init") else None

                        if subtype == 'DATA':
                            result = {
                                "init": init,
                                "tle_file" : path,
                                "satellites" : data.get("satellites"),
                                "num_tles" : data.get('num_tles'),
                                "sort_by" : data.get('sort_by'),
                                "timestamp" : data.get('timestamp'),
                                "last_saved" : data.get('last_saved'),
                            }

                        if subtype == 'CONFIG':
                            result = {
                                "init": init,
                                "config_file": path,
                                "lat" : data.get("lat"),
                                "lon" : data.get("lon"),
                                "timezone" : data.get("timezone"),
                                "radius" : data.get("radius"),
                                "loc_query" : data.get("loc_query"),
                                "loc_list" : data.get("loc_list"),
                                "loc_index" : data.get("loc_index"),
                                "tles" : data.get("tles"),
                                
                                "t0_max" : data.get("t0_max"),
                                "t1_max" : data.get("t1_max"),
                                
                                "filter" : data.get("filter"),
                                "classification" : data.get("classification"),
                                
                                "auto_save" : data.get("auto_save"),
                                "auto_save_interval" : data.get("auto_save_interval"),
                                "auto_download" : data.get("auto_download"),
                                "auto_download_interval" : data.get("auto_download_interval"),
                                "auto_simulate" : data.get("auto_simulate"),
                                "auto_sleep" : data.get("auto_sleep"),
                                "auto_render" : data.get("auto_render"),
                                
                                "sort_by": data.get("sort_by"),
                                "sleep_time": data.get("sleep_time"),
                                "wake_time": data.get("wake_time"),
                                
                                "auto_serial": data.get("auto_serial"),
                                "serial_port" : data.get("serial_port"),
                                "serial_baud" : data.get("serial_baud"),
                                "serial_value": data.get("serial_value"),

                                "pin_0_use": data.get("pin_0_use"),
                                "pin_0": data.get("pin_0"),
                                "pin_0_value": data.get("pin_0_value"), 
                                "pin_0_condition": data.get("pin_0_condition"),
                                
                                "pin_1_use": data.get("pin_1_use"),
                                "pin_1": data.get("pin_1"),
                                "pin_1_value": data.get("pin_1_value"),
                                "pin_1_condition": data.get("pin_1_condition"),
                                
                            
                                }   

                        f.close()

                    except FileNotFoundError as e:
                        print(e)
                    except json.decoder.JSONDecodeError as e:
                        print(e)
               
                msg = "%s File loaded: %s"%(time.strftime("%H:%M:%S"), path)
                if subtype:
                    msg = msg.replace("File", subtype.title())

                print(msg)    
                self.log(msg)
                
                if callback:
                    callback(data=result)
                
    def file_write(self, callback=None, **kwargs):
        path = kwargs.get('path')
        data = kwargs.get('data')
        subtype = kwargs.get('subtype')

        if not path:
            if subtype == 'CONFIG':
                path = self.properties.config_file
            
            if subtype == 'DATA':
                path = self.properties.tle_file
            
            if subtype == 'SESSION':
                path = self.properties.sessiondata_file

        if not data:
            if subtype == 'CONFIG':
                data = self.properties.properties_get()
            
            if subtype == 'DATA':
                data = self.trajectories.to_json()
            
            if subtype == 'SESSION':
                data = self.session_data()

        if path and data:
            with open(path, 'w', encoding='utf-8') as file:
                if type(data) == dict:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                elif type(data) == str:
                    file.write(data)
            file.close()

            msg = "%s File written: %s"%(time.strftime("%H:%M:%S"), path)
            if subtype:
                msg = msg.replace("File", subtype.title())

            print(msg)    
            self.log(msg)


        if callback:
            callback(True)


    ######## Url ########
    def url_request(self, url=None, callback=None):
        if url == None:
            url = DATAURL        

        msg = "%s Querying %s"%(time.strftime("%H:%M:%S"), url)
        print(msg)
        self.log(msg)

        data = requests.get(url)
    
        if data.status_code == 200:
            msg = "%s Download Finished"%(time.strftime("%H:%M:%S"))
            print(msg)
            self.log(msg)
            if callback:
                callback(data, mode='QUERY')

        elif data.status_code == 403:
            msg = "%s Request returned Code %i - Forbidden. Please wait for 2 hours"%(time.strftime("%H:%M:%S"), data.status_code)
            print(msg)
            self.log(msg)
        
        else:
            msg = "%s Request returned Code %i"%(time.strftime("%H:%M:%S"), data.status_code)
            print(msg)
            self.log(msg)
        
    def location_request(self, location):
        loc_list = []
        gn = geocoders.Nominatim(user_agent="strwüü")
        result = gn.geocode(location, exactly_one=False)

        if result:
            self.properties.loc_query_set(location)
            for i in range(len(result)):
                try:
                    lat = float(result[i][1][0])
                    lon = float(result[i][1][1])

                except ValueError:
                    timezone = None

                s = "%s, %s, %s"%(result[i][0], lat, lon)
                loc_list.append(s)

            self.properties.loc_list_set(loc_list) 
            self.properties.selection_set(0)

            # self.ui_q.put(Task(type='LOCATION_UPDATE', subtype='all', data=None))
            # self.ui_q.put(Task(type='SELECTION_UPDATE', subtype='MISC', data={}))
            
    def location_submit(self, location=None):
        if not location:
            location = self.properties.loc_query
        if location and location != '':
            self.input_q.put(Task(type='LOCATION_QUERY', callback=self.properties.selection_set, data=location))
            
    def timezone_request(self, data, callback):
        lat = data.get("lat")
        lon = data.get("lon")
        if lat and lon:
            obj = timezonefinder.TimezoneFinder()
            tz = obj.timezone_at(lng=lon, lat=lat)
            if tz and callback:
                callback(tz, single=False)

    ######## Serial ########
    def serial_open(self):
        port = self.properties.serial_port
        baud = self.properties.serial_baud
        if port and baud:

            try:
                ser = serial.Serial(port, baud, timeout=1)
                msg = "%s Serial port opened: %s"%(time.strftime("%H:%M:%S"), port)
                print(msg)
                self.log(msg)
                self.serial = ser
                self.ui_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_serial', data=None))
                if not self.trajectories.simulating:
                    self.input_q.put(Task(type='SERIAL_WRITE'))

            except serial.SerialException:
                self.serial = None
                msg = "%s Error: Serial port not found: %s"%(time.strftime("%H:%M:%S"), port)
                print(msg)
                self.log(msg)
            
    def serial_close(self):
        if self.serial:
            self.serial.close()
            self.serial = None
            msg = "%s Serial port closed: %s"%(time.strftime("%H:%M:%S"), self.properties.serial_port)
            print(msg)
            self.log(msg)

    def serial_write(self, data):
        if self.serial:
            if data != self.serial_data_previous:
                data = str(data)
                self.serial.write(data.encode('ascii'))
                time.sleep(0.01)
            self.serial_data_previous = data

        
    ######## Log ########
    def log_write(self, msg):
        # print(msg)
        pass

    def log(self, msg):
        self.input_q.put(Task(type='LOG_WRITE', message=msg))

    ######## IO ########

    def io_update(self, task):
        satellites_in_range = (len(self.trajectories.in_range) > 0)
        sleeping = self.sleeping

        if self.properties.pin_0_condition == "Satellites in Range":
            self.properties.pin_0_state_set(satellites_in_range * (self.properties.pin_0_value == 'High'))
        
        elif self.properties.pin_0_condition == "No Satellites in Range":
            self.properties.pin_0_state_set(not satellites_in_range * (self.properties.pin_0_value == 'High'))
        
        elif self.properties.pin_0_condition == "Sleeping":
            if sleeping:
                self.properties.pin_0_state_set(self.properties.pin_0_value == 'High')
            else:
                self.properties.pin_0_state_set(self.properties.pin_0_value == 'Low')

        elif self.properties.pin_0_condition == "Not Sleeping":
            if sleeping:
                self.properties.pin_0_state_set(self.properties.pin_0_value == 'Low')
            else:
                self.properties.pin_0_state_set(self.properties.pin_0_value == 'High')


        if self.properties.pin_1_condition == "Satellites in Range":
            self.properties.pin_1_state_set(satellites_in_range * (self.properties.pin_1_value == 'High'))
        
        elif self.properties.pin_1_condition == "No Satellites in Range":
            self.properties.pin_1_state_set(not satellites_in_range * (self.properties.pin_1_value == 'High'))
        
        elif self.properties.pin_1_condition == "Sleeping":
            if sleeping:
                self.properties.pin_1_state_set(self.properties.pin_1_value == 'High')
            else:
                self.properties.pin_1_state_set(self.properties.pin_1_value == 'Low')

        elif self.properties.pin_1_condition == "Not Sleeping":
            if sleeping:
                self.properties.pin_1_state_set(self.properties.pin_1_value == 'Low')
            else:
                self.properties.pin_1_state_set(self.properties.pin_1_value == 'High')

    def toggle_io_value(self, value):
        if value == gpiod.line.Value.INACTIVE:
            return gpiod.line.Value.ACTIVE
        return gpiod.line.Value.INACTIVE
    
    def toggle_line_value(self, chip_path, line_offset):
        value = gpiod.line.Value.ACTIVE

        with gpiod.request_lines(
                chip_path, 
                consumer="toggle_line_value", 
                config={
                    line_offset: gpiod.LineSettings(
                        direction=gpiod.line.Direction.OUTPUT, 
                        output_value=value
                        )}
        ) as line_request:
            value = self.toggle_io_value(value)
            line_request.set_value(line_offset, value)

    ######## Session ########
    def session_load(self):
        if self.properties.sessiondata_file:
            self.input_q.put(Task(type='FILE_READ', callback=self.session_set, subtype='SESSION', path=self.properties.sessiondata_file))

    def session_set(self, data):
        tles = data.get("tles")
        config = data.get("config")

        if config:
            self.load(config, init=True)
        else:
            self.properties.set_default()
         
        if tles:
            self.data_load(tles, init=True)

    def session_save(self):
        if self.properties.sessiondata_file:
            s = self.session_data()
            if s != '':
                self.input_q.put(Task(type='FILE_WRITE', 
                                      subtype='SESSION', 
                                      callback=None, 
                                      path=self.properties.sessiondata_file, 
                                      data=s)
                                      )

    def session_data(self):
        s = ''
        if self.properties.config_file:
            s += self.properties.config_file
        if self.properties.tle_file:
            s += '\n' + self.properties.tle_file
        return s

    ######## Config ########
    def load(self, path=None, init=False):
        if path == None:
            path = self.config_file
        self.input_q.put(Task(type='FILE_READ', callback=self.set, subtype='CONFIG', path=path, init=init))

    def set(self, data=None, default=False, **kwargs):
        if data or default == True:
            # init prevents saving due to value changes on load
            init = False
            if data:
                init = data.get("init") if data.get("init") else False
                self.properties.config_file_set(data.get("config_file"), single = not init) 
                self.properties.set_all(data)
                for key, value in self.properties.properties_get().items():
                    self.ui_q.put(Task(type='UI_UPDATE', subtype=key, data=None))
                
            else: # default == True
                self.properties.set_default()
                self.properties.config_file_set(None, single = False) 
                for key, value in self.properties.properties_get().items():
                    self.ui_q.put(Task(type='UI_UPDATE', subtype=key, data=None))

            self.input_q.put(Task(type='SIMULATION', subtype='selection'))
            self.input_q.put(Task(type='IO', subtype=None))
            
            if not init:
                self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='viewer'))
        
        self.input_q.put(Task(type='UI_UPDATE', subtype='sim_age'))

    def save(self, path=None):
        if path == None:
            path = self.properties.config_file
        else:
            self.properties.config_file_set(path, single = False) 

        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.properties.saved_set, path=path))
        self.ui_q.put(Task(type='UI_UPDATE', subtype='config_file'))
        self.ui_q.put(Task(type='UI_UPDATE', subtype='saved'))

    def new(self):
        self.set(data=None, default=True)
        self.properties.saved_set(False)
        self.ui_q.put(Task(type='UI_UPDATE', subtype='sim_age'))
        

    ######## Data ########
    def data_load(self, path, init=False):
        self.input_q.put(Task(type='FILE_READ', callback=self.data_set, subtype='DATA', path=path, init=init))
        
    def data_set(self, data, mode='DATA'):
        if self.trajectories and data:
            self.trajectories.tle_update(data, mode=mode)

        # init prevents saving due to value changes on load
        init = False
        if data:
            init = data.get("init") if data.get("init") else False
             
        self.properties.tle_file_set(data.get("tle_file"), single = not init)

        self.trajectories.update_once(update_coords=False, update_dist=True)
        self.ui_q.put(Task(type='FILE_UPDATE', subtype="tle_file", data=None))
        self.ui_q.put(Task(type='SIMULATION', subtype="sort_by", data=None))
        self.ui_q.put(Task(type='RENDERING', subtype="reset", data=None))
        self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='viewer', data=None))

        if self.properties.auto_simulate == True:
            self.simulation_start()

    def data_save(self, path=None):
        if path == None:
            path = self.properties.tle_file
        else:
            self.properties.tle_file_set(path)

        self.input_q.put(Task(type='FILE_WRITE', subtype='DATA', callback=self.trajectories.saved_set, path=path))
         
    def data_new(self):
        self.properties.tle_file_set(None, single=False)
        self.ui_q.put(Task(type='FILE_UPDATE', subtype='tle_file', data=None))
        self.input_q.put(Task(type='DATA_QUERY', url=None, callback=self.trajectories.tle_update))

    def data_refresh(self):
        self.input_q.put(Task(type='DATA_QUERY', url=None, callback=self.trajectories.tle_update))

    ######## Time ########
    def time_get(self, tz=False, mode='STR'):
        t = None
        if tz == False:
            t = self.time.gmtime()
        else:
            if self.properties.timezone:
                os.environ['TZ'] = self.properties.timezone
                self.time.tzset()
            t = self.time.localtime()

        if mode == 'STR':
            return  self.time.strftime("%H:%M:%S",t)
        else:
            return t


class ConfigData():
    def __init__(self, input_q, ui_q):
        #### Queue ####
        self.input_q = input_q
        self.ui_q = ui_q
        #### Files ####
        file = os.path.join(os.path.dirname(__file__), '../sessiondata')
        self.sessiondata_file = file if os.path.isfile(file) else None    
       
        self.config_file = None
        self.tle_file = None
        
        #### Location ####
        self.lat = None
        self.lon = None
        self.timezone = None
        
        self.loc_query = None
        self.loc_list = []
        self.loc_index = 0        
        
        #### Filter ####
        self.radius = None
        self.classification = None
        self.filter = []
        
        #### Simulation ####
        self.sort_by = None
        self.t0_max = 0
        self.t1_max = 0
        
        #### Automation ####
        self.auto_save = False
        self.auto_save_interval = 0

        self.auto_download = False
        self.auto_download_interval = 0
        
        self.auto_simulate = None
        self.auto_render = None
        self.auto_sleep = None
        self.auto_serial = None

        self.sleep_time = None
        self.wake_time = None
        
        self.serial_port = None
        self.serial_baud = None
        self.serial_value = None
        
        self.pin_0_use = False
        self.pin_0 = 0
        self.pin_0_value = 'High'
        self.pin_0_condition = False
        self.pin_0_state = False # LO
        self.pin_0_line = None

        self.pin_1_use = False
        self.pin_1 = 1
        self.pin_1_value = 'High'
        self.pin_1_condition = False
        self.pin_1_state = False # LO
        self.pin_1_line = None

                #### Save state ####
        self.saved = True
        self.sort_by = None

        self.default_values = {
            "sessiondata_file" : "", 
            "config_file" : "",
            "tle_file" : "",
            "lat" : None,
            "lon" : None,
            "timezone" : None,
            "radius" : 500,
            "loc_query" : "",
            "loc_list" : [],
            "loc_index" : 0,        
            "t0_max" : 128,
            "t1_max" : 12800,
            "filter" : [],
            "classification" : 'Unclassified',
            "serial_port" : 0,
            "serial_baud" : 0,
            "serial_value" : None,
            "auto_save" : False,
            "auto_save_interval" : 30,
            "auto_download" : False,
            "auto_download_interval" : 4,
            "auto_simulate" : False,
            "auto_sleep" : False,
            "auto_serial" : False,
            "auto_render" : False,

            "pin_0_use": False,
            "pin_0": 0,
            "pin_0_value": 'High',
            "pin_0_condition": False,

            "pin_1_use": False,
            "pin_1": 1,
            "pin_1_value": 'High',
            "pin_1_condition": False,

            "wake_time": "00:00",
            "sleep_time": "00:00",


            "saved" : True, 
            "sort_by": "Proximity"
        }


    def properties_get(self):
        data = {
                "sessiondata_file" : self.sessiondata_file, 
                "config_file" : self.config_file,
                "tle_file" : self.tle_file,
                "lat" : self.lat,
                "lon" : self.lon,
                "timezone" : self.timezone,
                "radius" : self.radius,
                "loc_query" : self.loc_query,
                "loc_list" : self.loc_list,
                "loc_index" : self.loc_index,        
                "t0_max" : self.t0_max,
                "t1_max" : self.t1_max,
                "filter" : self.filter,
                "classification" : self.classification,
                "serial_port" : self.serial_port,
                "serial_baud" : self.serial_baud,
                "serial_value" : self.serial_value,
                "auto_save" : self.auto_save,
                "auto_save_interval" : self.auto_save_interval,
                "auto_download" : self.auto_download,
                "auto_download_interval" : self.auto_download_interval,
                "auto_simulate" : self.auto_simulate,
                "auto_sleep" : self.auto_sleep,
                "auto_serial" : self.auto_serial,
                "auto_render" : self.auto_render,
                "sort_by" : self.sort_by, 
                
                "sleep_time": self.sleep_time,
                "wake_time": self.wake_time,

                "pin_0_use": self.pin_0_use,
                "pin_0": self.pin_0,
                "pin_0_value": self.pin_0_value,
                "pin_0_condition": self.pin_0_condition,

                "pin_1_use": self.pin_1_use,
                "pin_1": self.pin_1,
                "pin_1_value": self.pin_1_value,
                "pin_1_condition": self.pin_1_condition,
        }
        return data
    
    def get(self, value):
        data = self.properties_get()
        result = data.get(value)
        return result

    def set_default(self):
        
        self.loc_query_set(self.default_values["loc_query"], single=False)
        self.loc_list_set(self.default_values["loc_list"], single=False)
        
        self.selection_set(self.default_values["loc_index"], single=False)
    
        self.radius_set(self.default_values["radius"], single=False)
        self.t0_max_set(self.default_values["t0_max"], single=False)
        self.t1_max_set(self.default_values["t1_max"], single=False)
        self.filter_set(self.default_values["filter"], single=False)
        self.classification_set(self.default_values["classification"], single=False)
        self.serial_port_set(self.default_values["serial_port"], single=False)
        self.serial_baud_set(self.default_values["serial_baud"], single=False)
        self.serial_value_set(self.default_values["serial_value"], single=False)
        self.auto_save_set(self.default_values["auto_save"], single=False)
        self.auto_save_interval_set(self.default_values["auto_save_interval"], single=False)
        self.auto_download_set(self.default_values["auto_download"], single=False)
        self.auto_download_interval_set(self.default_values["auto_download_interval"], single=False)
        self.auto_simulate_set(self.default_values["auto_simulate"], single=False)
        self.auto_sleep_set(self.default_values["auto_sleep"], single=False)
        self.auto_serial_set(self.default_values["auto_serial"], single=False)
        self.auto_render_set(self.default_values["auto_render"], single=False)
        self.sort_by_set(self.default_values["sort_by"], single=False)
        
        self.pin_0_use_set(self.default_values["pin_0_use"], single=False)
        self.pin_0_set(self.default_values["pin_0"], single=False)
        self.pin_0_value_set(self.default_values["pin_0_value"], single=False)
        self.pin_0_condition_set(self.default_values["pin_0_condition"], single=False)
        
        self.pin_1_use_set(self.default_values["pin_1_use"], single=False)
        self.pin_1_set(self.default_values["pin_1"], single=False)
        self.pin_1_value_set(self.default_values["pin_1_value"], single=False)
        self.pin_1_condition_set(self.default_values["pin_1_condition"], single=False)

        self.sleep_time_set(self.default_values["sleep_time"], single=False)
        self.wake_time_set(self.default_values["wake_time"], single=False)
        
    def set_all(self, data):

        loc_query = data.get("loc_query")
        self.loc_query_set(loc_query if loc_query else self.default_values["loc_query"], single=False)
        
        loc_list = data.get("loc_list")
        self.loc_list_set(loc_list if loc_list else self.default_values["loc_list"], single=False)

        
        loc_index = data.get("loc_index")
        self.selection_set(loc_index, single=False)
        
        
        radius = data.get("radius")
        self.radius_set(radius if radius else self.default_values["radius"], single=False)
        

        
        t0_max = data.get("t0_max")
        self.t0_max_set(t0_max if t0_max else self.default_values["t0_max"], single=False)
        
        t1_max = data.get("t1_max")
        self.t1_max_set(t1_max if t1_max else self.default_values["t1_max"], single=False)
        
        filter = data.get("filter")
        self.filter_set([f for f in filter] if filter else self.default_values["filter"], single=False)
        
        classification = data.get("classification")
        self.classification_set(classification if classification else self.default_values["classification"], single=False)
        
        serial_port = data.get("serial_port")
        self.serial_port_set(serial_port if serial_port else self.default_values["serial_port"], single=False)
        
        serial_baud = data.get("serial_baud")
        self.serial_baud_set(serial_baud if serial_baud else self.default_values["serial_baud"], single=False)
        
        serial_value = data.get("serial_value")
        self.serial_value_set(serial_value if serial_value else self.default_values["serial_value"], single=False)
        
        auto_save = data.get("auto_save")
        self.auto_save_set(auto_save if auto_save else self.default_values["auto_save"], single=False)
       

        auto_save_interval = data.get("auto_save_interval")
        self.auto_save_interval_set(auto_save_interval if auto_save_interval else self.default_values["auto_save_interval"], single=False)
        
        auto_download = data.get("auto_download")
        self.auto_download_set(auto_download if auto_download else self.default_values["auto_download"], single=False)
        
        auto_download_interval = data.get("auto_download_interval")
        self.auto_download_interval_set(auto_download_interval if auto_download_interval else self.default_values["auto_download_interval"], single=False)
        
        auto_simulate = data.get("auto_simulate")
        self.auto_simulate_set(auto_simulate if auto_simulate else self.default_values["auto_simulate"], single=False)
        
        auto_sleep = data.get("auto_sleep")
        self.auto_sleep_set(auto_sleep if auto_sleep else self.default_values["auto_sleep"], single=False)

        auto_serial = data.get("auto_serial")
        self.auto_serial_set(auto_serial if auto_serial else self.default_values["auto_serial"], single=False)

        
        auto_render = data.get("auto_render")
        self.auto_render_set(auto_render if auto_render else self.default_values["auto_render"], single=False)

        sort_by = data.get("sort_by")
        self.sort_by_set(sort_by if sort_by else self.default_values["sort_by"], single=False)

        sleep_time = data.get("sleep_time")
        self.sleep_time_set(sleep_time, single=False)

        wake_time = data.get("wake_time")
        self.wake_time_set(wake_time, single=False)

        pin_0_use = data.get("pin_0_use")
        self.pin_0_use_set(pin_0_use, single=False)
        
        pin_0 = data.get("pin_0")
        self.pin_0_set(pin_0, single=False)
        
        pin_0_value = data.get("pin_0_value")
        self.pin_0_value_set(pin_0_value, single=False)
        
        pin_0_condition = data.get("pin_0_condition")
        self.pin_0_condition_set(pin_0_condition, single=False)
        
        pin_1_use = data.get("pin_1_use")
        self.pin_1_use_set(pin_1_use, single=False)
        
        pin_1 = data.get("pin_1")
        self.pin_1_set(pin_1, single=False)
        
        pin_1_value = data.get("pin_1_value")
        self.pin_1_value_set(pin_1_value, single=False)
        
        pin_1_condition = data.get("pin_1_condition")
        self.pin_1_condition_set(pin_1_condition, single=False)
        

    
    #### Files ####
    def sessiondata_file_set(self, value, single=True):
        self.sessiondata_file = value
                   
    def tle_file_set(self, value, single=True):
        if self.tle_file != value:
            if type(value == str):
                self.tle_file = value
            if single == True and self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                self.input_q.put(Task(type='FILE_WRITE', subtype='SESSION'))
            
            self.ui_q.put(Task(type='FILE_UPDATE', subtype='tle_file'))
          
    def config_file_set(self, value, single=True):
        if self.config_file != value:
            self.config_file = value
            if single == True and self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                self.input_q.put(Task(type='FILE_WRITE', subtype='SESSION'))
            
            self.ui_q.put(Task(type='FILE_UPDATE', subtype='config_file'))
        if value == None:
            self.saved_set(False)
        

    #### Location ####
    def lat_set(self, value, single=True):
        if self.lat != value:
            if type(value == float):
                self.lat = value
                if single == True:
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                    else:
                        self.saved_set(False)
        
    def lon_set(self, value, single=True):
        if self.lon != value:
            if type(value == float):
                self.lon = value
                if single == True:
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                    else:
                        self.saved_set(False)

    def timezone_set(self, value, single=True):
        self.timezone = value
        
        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
            else:
                self.saved_set(False)
        self.input_q.put(Task(type='SIMULATION_UPDATE', subtype='timezone'))
        self.ui_q.put(Task(type='SELECTION_UPDATE', subtype='timezone', data=None))
            
    def loc_query_set(self, value, single=True):
        if self.loc_query != value and value != None:
            self.loc_query = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)
            
    def loc_list_set(self, value, single=True):
        self.loc_list = value
        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
            else:
                self.saved_set(False)
            
    def loc_index_set(self, value, single=True):
        if self.loc_index != value and value != None: 
            self.loc_index = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)

    def selection_set(self, selection_index, single=True):
        self.loc_index_set(selection_index, single=False)
        try:
            txt = [i.strip() for i in self.loc_list[selection_index].split(',')]
            lon = float(txt.pop())
            lat = float(txt.pop())

            if lat and lon:
                self.lon_set(lon, single=False)
                self.lat_set(lat, single=False)
                self.input_q.put(Task(type='TIMEZONE_QUERY', callback=self.timezone_set, data={'lat':lat, 'lon':lon}))
            
            self.input_q.put(Task(type='SIMULATION', subtype='selection'))
                
            country = txt.pop() if len(txt) > 0 else None
            zip_code = txt.pop() if len(txt) > 0 else None
            district = txt.pop() if len(txt) > 0 else None
            city = txt.pop() if len(txt) > 0 else None
            selected = txt.pop() if len(txt) > 0 else None            

            additional_data = {
                "lat": lat,
                "lon": lon,
                "country" : country,
                "zip" : zip_code,
                "distr" : district,
                "city" : city,
                "selected" : selected,
            }

            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)



            self.ui_q.put(Task(type='SELECTION_UPDATE', subtype='MISC', data=additional_data))
        
        except IndexError:
            self.timezone_set(None) # List empty
            self.ui_q.put(Task(type='SELECTION_UPDATE', subtype='MISC', data={}))

        self.ui_q.put(Task(type='LOCATION_UPDATE', subtype='all'))
        
        if single:
            if self.auto_render:
                self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='viewer'))


    #### Filter ####
    def radius_set(self, value, single=True):
        if self.radius != value and value != None:
            self.radius = value

            if single == True:
                self.input_q.put(Task(type='SIMULATION', subtype='radius'))
                if self.auto_render:
                    self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)
              
    def classification_set(self, value, single=True):
        if self.classification != value and value != None:
            self.classification = value

            
            if single == True:
                self.input_q.put(Task(type='SIMULATION', subtype='classification'))
                if self.auto_render:
                    self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)
            
    def filter_set(self, value, single=True):
        if not type(value) == list:
            value = [value]

        if value != self.filter:
            if self.filter != value and value != None:
                self.filter = value


                if single == True:
                    self.input_q.put(Task(type='SIMULATION', subtype='filter'))
                    if self.auto_render:
                        self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                    else:
                        self.saved_set(False)
    

    #### Simulation ####
    def sort_by_set(self, value, single=True):
        if value != self.sort_by:
            self.sort_by = value
            self.input_q.put(Task(type='SIMULATION', subtype='sort_by'))
            if single == True:
                if self.auto_render:
                    self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                else:
                    self.saved_set(False)
            
    def t0_max_set(self, value, single=True):
        if self.t0_max != value:
            try:
                value = int(value)
                self.t0_max = value
                if single == True:
                    if self.auto_render:
                        self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                    else:
                        self.saved_set(False)

                return value
                
            except ValueError:
                return False

        return False

    def t1_max_set(self, value, single=True):
        if self.t1_max != value:
            try:
                value = int(value)
                self.t1_max = value
                self.input_q.put(Task(type='SIMULATION', subtype='threads'))
                if single == True:
                    if self.auto_render:
                        self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='threads'))
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG'))
                    else:
                        self.saved_set(False)

                return value

            except ValueError:
                return False
        return False


    #### Automation ####
    def auto_save_set(self, value, single=True):
        self.auto_save = value
        if single == True:
            self.ui_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_save'))
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
            
    def auto_save_interval_set(self, value, single=True):
        if value != self.auto_save_interval: 
            self.auto_save_interval = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
                    
    def auto_download_set(self, value, single=True):
        if self.auto_download != value and value != None:
            self.auto_download = value
            if single == True:
                self.ui_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_download'))
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            
    def auto_download_interval_set(self, value, single=True):
        if self.auto_download_interval != value and value != None:
            self.auto_download_interval = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            
    def auto_simulate_set(self, value, single=True):
        if self.auto_simulate != value and value != None:
            self.auto_simulate = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            
    def auto_sleep_set(self, value, single=True):
        if self.auto_sleep != value and value != None:
            self.auto_sleep = value
            self.input_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_sleep'))
            if single == True:
                self.ui_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_sleep'))

                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            
    def auto_render_set(self, value, single=True):
        self.auto_render = value
        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
            if value == True:
                self.ui_q.put(Task(type='VIEWER_UPDATE', subtype='viewer'))
            
    def wake_time_set(self, value, single=True):
        try:
            divisor = None
            hours = None
            minutes = None

            for item in [':', '.', '-']:
                if item in value:
                    divisor = item
            if divisor:
                strtime = value.split(divisor)
                hours = int(strtime[0].strip())
                minutes = int(strtime[1].strip())
            else:
                minutes = int(value[-2:])
                hours = int(value[:1] if len(value)==3 else value[:2])

            if hours !=None and hours < 24:
                if minutes != None and minutes < 60:
                    strtime = str(hours).zfill(2) + ':' + str(minutes).zfill(2)
                    if self.wake_time != strtime:
                        self.wake_time = strtime
                        if single == True:
                            if self.auto_save:
                                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                            else:
                                self.saved_set(False)
                        
                        self.input_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_sleep'))
                        return strtime

            return False

        except ValueError:
            return False
        
        except IndexError:
            return False

        except TypeError:
            return False

    def sleep_time_set(self, value, single=True):
        try:
            divisor = None
            hours = None
            minutes = None

            for item in [':', '.', '-']:
                if item in value:
                    divisor = item
            if divisor:
                strtime = value.split(divisor)
                hours = int(strtime[0].strip())
                minutes = int(strtime[1].strip())
            else:
                minutes = int(value[-2:])
                hours = int(value[:1] if len(value)==3 else value[:2])

            if hours !=None and hours < 24:
                if minutes !=None and minutes < 60:
                    strtime = str(hours).zfill(2) + ':' + str(minutes).zfill(2)
                    if self.sleep_time != strtime:
                        self.sleep_time = strtime
                        if single == True:
                            if self.auto_save:
                                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                            else:
                                self.saved_set(False)
                        
                        self.input_q.put(Task(type='AUTOMATION_UPDATE', subtype='auto_sleep'))
                        return strtime
                    
            return False

        except ValueError:
            return False
        
        except IndexError:
            return False

        except TypeError:
            return False
            

    #### Pins ####
    def pin_0_use_set(self, value, single=True):
        self.pin_0_use = value      
        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
   
    def pin_0_set(self, value, single=True):
        if type(value) == int and value < 0 and value > 25:
            self.pin_0 = value

        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
   
    def pin_0_value_set(self, value, single=True):
        self.pin_0_value = value
        if single == True:
            self.input_q.put(Task(type='IO', subtype=None))
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
         
    def pin_0_condition_set(self, value, single=True):
        self.pin_0_condition = value
        if single == True:
            self.input_q.put(Task(type='IO', subtype=None))
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)


    def pin_0_state_set(self, value):
        if value != self.pin_0_state:
            if self.pin_0_line:
                self.pin_0_line.set_value(int(value))

            if value == 0:
                value = False
            elif value == 1:
                value = True
            self.pin_0_state = value
            self.ui_q.put(Task(type='UI_UPDATE', subtype='pin_0_state'))

    def pin_1_use_set(self, value, single=True):
        self.pin_1_use = value
        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)


    def pin_1_set(self, value, single=True):
        if type(value) == int and value < 0 and value > 25:
            self.pin_1 = value
                
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)


    def pin_1_value_set(self, value, single=True):
        self.pin_1_value = value
        if single == True:
            self.input_q.put(Task(type='IO', subtype=None))
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)

    def pin_1_condition_set(self, value, single=True):
        self.pin_1_condition = value
        if single == True:
            self.input_q.put(Task(type='IO', subtype=None))
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)

    def pin_1_state_set(self, value):
        if value != self.pin_1_state:
            if value == 0:
                value = False
            elif value == 1:
                value = True
            self.pin_1_state = value
            self.ui_q.put(Task(type='UI_UPDATE', subtype='pin_1_state'))

        


    #### Serial ####
    def auto_serial_set(self, value, single=True):
        self.auto_serial = value

        if value == True:
            self.input_q.put(Task(type='SERIAL_OPEN'))
        else:
            self.input_q.put(Task(type='SERIAL_CLOSE'))

        if single == True:
            if self.auto_save:
                self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
            else:
                self.saved_set(False)
            
   
    def serial_value_set(self, value, single=True):
        if self.serial_value != value and value != None:
            self.serial_value = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            

    def serial_port_set(self, value, single=True):
        if self.serial_port != value and value != None:
            self.serial_port = value
            if single == True:
                if self.auto_save:
                    self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                else:
                    self.saved_set(False)
            
    
    def serial_baud_set(self, value, single=True):
        if self.serial_baud != value and value != None:
            try:
                value = int(value)
                self.serial_baud = value
                if single == True:
                    if self.auto_save:
                        self.input_q.put(Task(type='FILE_WRITE', subtype='CONFIG', callback=self.saved_set))
                    else:
                        self.saved_set(False)

            except ValueError:
                msg = "%s Invalid Baud Rate: %s"%(time.strftime("%H:%M:%S"), value)
                print(msg)
                self.input_q.put(Task(type='LOG_WRITE', message=msg))
                self.ui_q.put(Task(type='OUTPUT_UPDATE', subtype='serial_baud'))


    def saved_set(self, value):
        if value == None:
            value = True
        self.saved = value
        self.input_q.put(Task(type='INFO_UPDATE', subtype='saved'))


   