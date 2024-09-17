#!/home/schnollie/.venvs/strwueue/bin/python
import time
import os
import pathlib
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
from tkinter import ttk
from style import style as strwueuestyle


RESOLUTION_X = 800
RESOLUTION_Y = 600


class LocationBox(ttk.Frame):
    def __init__(self, root, config):
        self.config = config
        self.root = root

        self.location = tk.StringVar()
        self.frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.frame.pack(padx=0, pady=(4,0), fill='both', expand=True)

        location_label = ttk.Label(self.frame, text="Location:", style="BoldDark.TLabel")
        self.location_entry = ttk.Entry(self.frame, textvariable=self.location, style="Dark.TEntry")
        self.location_entry.bind('<Return>', self.location_submit)

        location_button = ttk.Button(self.frame, text="OK", command=self.location_submit, style="Dark.TButton")
        self.loc_list_ui = tk.Listbox(self.frame, selectmode = tk.BROWSE, exportselection=False, width=66)
        self.loc_list_ui.bind('<<ListboxSelect>>', self.location_set)
        self.loc_list_ui.bind('<Return>', self.location_set)

        location_label.grid(row=0, column=0, sticky='E')
        self.location_entry.grid(row=0, column=1, columnspan=5, padx=2, pady=2, sticky="EW")
        location_button.grid(row=0, column=6, padx=2, pady=2)
        
        self.loc_list_ui.grid(row=1, column=1, columnspan=6, rowspan=8, padx=2, pady=2, sticky='EW')

        self.frame.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=1)
        

    def location_submit(self, event=None):
        self.config.location_submit(self.location.get())



    def location_set(self, event, selection_index=None): 
        index = 0
        if selection_index != None:
            index = selection_index
        else:
            try:
                selection = event.widget.curselection()
                if len(selection) > 0:
                    index = selection[0]

            except AttributeError:
                pass

        self.config.properties.selection_set(index)


    def update(self, task):

        if task.subtype == 'loc_list' or task.subtype == 'all':
            if self.config.properties.loc_list:
                loc_list = self.config.properties.loc_list
                loc_index = self.config.properties.loc_index if self.config.properties.loc_index else 0

                self.loc_list_ui.delete(0, tk.END)

                for i in range(len(loc_list)):
                    s =  loc_list[i]
                    self.loc_list_ui.insert(tk.END, s) 
                    self.loc_list_ui.itemconfig(i, 
                            bg = "grey20" if i % 2 == 0 else "grey10",
                            fg="grey50")     

                self.loc_list_ui.select_clear(0, "end")
                self.loc_list_ui.selection_set(loc_index)
                self.loc_list_ui.see(loc_index)
                self.loc_list_ui.activate(loc_index)
                self.loc_list_ui.selection_anchor(loc_index)
            else:
                self.loc_list_ui.delete(0, tk.END)

        if task.subtype == 'loc_query' or task.subtype == 'all':
            if self.config.properties.loc_query:
                self.location.set(self.config.properties.loc_query)
            else:
                self.location.set("")


        
          

class SelectionBox(ttk.Frame):
    def __init__(self, root, config):
        self.config = config
        self.root = root
        frame = ttk.Frame(root, style="Dark.TFrame")
        frame.pack(padx=0, pady=(4,0), fill='both', expand=True)

        selected_label = ttk.Label(frame, text="Selection:", style="BoldDark.TLabel")
        selected_label.grid(row=0, column=0, sticky="E", padx=(0,4))
        self.selected = ttk.Label(frame, text="", style="Dark.TLabel")
        self.selected.grid(row=0, column=1, sticky="W")
        
        city_label = ttk.Label(frame, text="City:", style="BoldDark.TLabel")
        city_label.grid(row=1, column=0, sticky="E", padx=(0,4))
        self.city = ttk.Label(frame, text="", style="Dark.TLabel")
        self.city.grid(row=1, column=1, sticky="W")

        country_label = ttk.Label(frame, text="Country:", style="BoldDark.TLabel")
        country_label.grid(row=2, column=0, sticky="E", padx=(0,4))
        self.country = ttk.Label(frame, text="", style="Dark.TLabel")
        self.country.grid(row=2, column=1, sticky="W")

        timezone_label = ttk.Label(frame, text="Time zone:", style="BoldDark.TLabel")
        self.timezone = ttk.Label(frame, text="", style="Dark.TLabel")
        timezone_label.grid(row=0, column=2, sticky="E")
        self.timezone.grid(row=0, column=3, sticky="W")

        lat_label = ttk.Label(frame, text="Latitude:", style="BoldDark.TLabel")
        self.lat = ttk.Label(frame, text="", style="Dark.TLabel")
        lat_label.grid(row=1, column=2, sticky="E")
        self.lat.grid(row=1, column=3, sticky="W")

        lon_label = ttk.Label(frame, text="Longitude:", style="BoldDark.TLabel")
        self.lon = ttk.Label(frame, text="", style="Dark.TLabel")
        lon_label.grid(row=2, column=2, sticky="E")
        self.lon.grid(row=2, column=3, sticky="W")
        

        clock_label = ttk.Label(frame, text="Local Time:", style="BoldDark.TLabel")
        clock_label.grid(row=4, column=0, sticky="E", padx=(0,4))
        self.clock = ttk.Label(frame, text="00:00", style="Dark.TLabel")
        self.clock.grid(row=4, column=1, sticky="WE", ipadx=50)

        sleeping_label = ttk.Label(frame, text="Sleeping:", style="BoldDark.TLabel")
        sleeping_label.grid(row=4, column=2, sticky="E")
        self.sleeping = ttk.Label(frame, text="False", style="Dark.TLabel")
        self.sleeping.grid(row=4, column=3, sticky="W")

        frame.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=0)
        self.clock_tick()


    def clock_tick(self):
        t = self.config.time_get(tz=True, mode='STR')
        self.clock.configure(text = t)
        self.root.after(1000, self.clock_tick)


    def update(self, task):
        
        if task.subtype == 'timezone':
            if self.config.properties.timezone:
                self.timezone.configure(text=self.config.properties.timezone)
            else:
                self.timezone.configure(text="")
                
        if task.subtype == 'sleep':
            self.sleeping.configure(text=str(self.config.sleeping))

        if task.subtype == 'MISC':
            if 'lat' in task.data:
                self.lat.configure(text=self.config.properties.lat)
            else:
                self.lat.configure(text="")

            if 'lon' in task.data:
                self.lon.configure(text=self.config.properties.lon)
            else:
                self.lon.configure(text="")

            if 'selected' in task.data:
                self.selected.configure(text=task.data['selected'])
            else:
                self.selected.configure(text="")

            if 'country' in task.data:
                self.country.configure(text=task.data['country'])
            else:
                self.country.configure(text="")

            if 'city' in task.data:
                self.city.configure(text=task.data['city'])
            else:
                self.city.configure(text="")
            
            

class FileBox(ttk.Frame):
    def __init__(self, root, config):
        self.config = config
        self.root = root
        self.sim_age = "0 minutes"
        self.tle_age = "0 hours"

        frame = ttk.Frame(root, style="Dark.TFrame")
        frame.pack(padx=0, pady=(4,0), fill='both', expand=True)
        config_row = 0
        tle_row = 1
        info_row_0 = 4
        
        ################################ CONFIG ################################
        config_label = ttk.Label(frame, text="Config:", style="BoldDark.TLabel")
        config_label.grid(row=config_row, column=0, sticky="E", padx=(0,4))
        self.config_open_button = ttk.Button(frame, text="Open", command=self.config_open, style="Dark.TButton")
        self.config_open_button.grid(row=config_row, column=1, columnspan=4, sticky='EW', padx=0)

        config_get_button = ttk.Button(frame, text="New", command=self.config_new, style="Dark.TButton")
        config_get_button.grid(row=config_row, column=5, sticky='WE', padx=0)

        config_save_button = ttk.Button(frame, text="Save", command=self.config_save, style="Dark.TButton")
        config_save_button.grid(row=config_row, column=6, sticky='W', padx=0)

        ################################ TLE ################################
        tle_label = ttk.Label(frame, text="Data:", style="BoldDark.TLabel")
        tle_label.grid(row=tle_row, column=0, sticky="E", padx=(0,4))
        self.tle_open_button = ttk.Button(frame, text="Open", command=self.tle_open, style="Dark.TButton")
        self.tle_open_button.grid(row=tle_row, column=1, columnspan=4, sticky='EW', padx=0)

        tle_get_button = ttk.Button(frame, text="New", command=self.tle_new, style="Dark.TButton")
        tle_get_button.grid(row=tle_row, column=5, sticky='WE', padx=0)

        tle_save_button = ttk.Button(frame, text="Save", command=self.tle_save, style="Dark.TButton")
        tle_save_button.grid(row=tle_row, column=6, sticky='W', padx=0)

        ################################ INFO ################################ 
        info_0_label = ttk.Label(frame, text="Info:", style="BoldDark.TLabel")
        info_0_label.grid(row=info_row_0, column=0, rowspan=1, sticky="E", padx=(0,4))

        self.info_0_val = ttk.Label(frame, text="0 satellites and 0 trajectories in cache.", style="Dark.TLabel")
        self.info_0_val.grid(row=info_row_0, column=1, columnspan=6, sticky="W")
        frame.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=1)    


    def update(self, task):
        
        if task.subtype == 'config_file':
            if self.config.properties.config_file:
                self.config_open_button.configure(text=self.config.properties.config_file)
            else:
                self.config_open_button.configure(text="Open")


        if task.subtype == 'tle_file':
            if self.config.properties.tle_file:
                self.tle_open_button.configure(text=self.config.properties.tle_file)
            else:
                self.tle_open_button.configure(text="Open")

        # if task.subtype == 'sim_age' or task.subtype == 'tle_age':
        if task.subtype == 'sim_age':
            self.sim_age = str(self.config.trajectories.sim_age).strip("'(),")
            if self.sim_age[0] == '1':
                self.sim_age = self.sim_age.replace("minutes", "minute")

        if task.subtype == 'tle_age':
            self.tle_age = str(self.config.trajectories.tle_age).strip("'(),")
            if self.tle_age[0] == '1':
                self.tle_age = self.tle_age.replace("hours", "hour")

        num_tles = 0 if type(self.config.trajectories.num_tles) != int else self.config.trajectories.num_tles
        config_saved = self.config.properties.get("saved")
        tle_file = self.config.properties.get("tle_file")
        tle_saved = self.config.properties.get("saved")

        if tle_file:
            info  = "%i satellites in cache, saved %s ago "%(num_tles, self.sim_age)
        else:
            info  = "%i satellites in cache, unsaved "%num_tles

        info += "| Config %s "%("saved" if config_saved == True else "unsaved")
        info += "| Data decay: %s"%str(self.tle_age)

        self.info_0_val.configure(text=info)
 
        

    def config_new(self):
        self.config.new()


    def config_open(self):
        filename = askopenfilename(title="Load Config")
        if filename:
            self.config.load(filename)
  

    def config_save(self):
        filename = asksaveasfile(title="Save Config as")
        if filename:
            self.config.save(filename.name)
            

    def tle_new(self):
        self.config.data_new()


    def tle_open(self):
        filename = askopenfilename(title="Load Data")
        if filename:
            self.config.data_load(filename)

    def tle_save(self):
        filename = asksaveasfile(title="Save Data as")
        if filename:
            self.config.data_save(filename.name)


class OptionBox(ttk.Frame):
    def __init__(self, root, config):
        self.config = config
        self.root = root

        self.radius = tk.IntVar()
        self.filter = tk.StringVar()
        self.classification = tk.StringVar()

        self.frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.frame.pack(padx=0, pady=(4,0), fill='both', expand=True)

        ################################ RADIUS ################################
        radius_label = ttk.Label(self.frame, text="Radius(km):", style="BoldDark.TLabel")
        radius_label.grid(row=0, column=0, sticky="E", padx=(0,4))
        self.choices_radius = [0, 0.001, 0.01, 0.1, 1, 10, 50, 100, 200, 500, 1000, 1500, 2000, 4000, 8000]
        
        radius_box = ttk.OptionMenu(self.frame, self.radius, *self.choices_radius, command=self.radius_set, style="Dark.TMenubutton")
        radius_box.grid(row=0, column=1, sticky='W')
        self.radius.set(self.choices_radius[3])
        
        ################################ CLASSIFICATION ################################
        classification_label = ttk.Label(self.frame, text="Class:", style="BoldDark.TLabel")
        classification_label.grid(row=0, column=2, sticky="E")
        self.choices_class = ['Classification', 'All', 'Unclassified', 'Classified', 'Secret']
        classification_box = ttk.OptionMenu(self.frame, self.classification, *self.choices_class, command=self.classification_set, style="Dark.TMenubutton")
        classification_box.grid(row=0, column=3, sticky='W')
        self.classification.set(self.choices_class[1])
        
        ################################ FILTERS ################################
        filter_label = ttk.Label(self.frame, text="Filter:", style="BoldDark.TLabel")
        filter_label.grid(row=0, column=4, sticky="E")
        
        filter_box = ttk.Entry(self.frame, textvariable=self.filter, validate="focusout", validatecommand=self.filter_set, style="Dark.TEntry")
        filter_box.bind('<Return>', self.filter_set)
        filter_box.grid(row=0, column=5, columnspan=2, sticky='EW', padx=(0,100))

        self.frame.columnconfigure((0,1,2,3,4),minsize=100, weight=0)
        self.frame.columnconfigure((5),minsize=200, weight=1)



    def update(self, task):
        if task.subtype == 'radius':
            index = 0
            for i in range(len(self.choices_radius)):
                if self.config.properties.radius == self.choices_radius[i]:
                    index = i
            self.radius.set(self.choices_radius[index])

        if task.subtype == 'class':
            index = 0
            for i in range(len(self.choices_class)):
                if self.config.properties.classification == self.choices_class[i]:
                    index = i
            self.radius.set(self.choices_radius[index])

        if task.subtype == 'filter':
            self.filter.set(", ".join(self.config.properties.filter))
        

    def radius_set(self, event):
        self.config.properties.radius_set(self.radius.get())
        
    def classification_set(self, event):
        self.config.properties.classification_set(self.classification.get())
        
    def filter_set(self, event=None):
        self.config.properties.filter_set(self.filter.get())
        

class SimulationBox(ttk.Frame):
    def __init__(self, root, config, viewer=None):
        self.viewer = viewer
        self.root = root
        self.config = config

        self.sort_by = tk.StringVar()
        self.t0_max = tk.StringVar()
        self.t1_max = tk.StringVar()

        self.frame = ttk.Frame(self.root, style="Dark.TFrame")
        
        simulation_label = ttk.Label(self.frame, text="Simulation:", style="BoldDark.TLabel")
        simulation_label.grid(row=0, column=0, sticky="E", padx=(0,4))
        self.run_button = ttk.Button(self.frame, text="Start", command=self.sim_toggle, style="Dark.TButton")
        self.run_button.grid(row=0, column=1, sticky='EW', padx=0)

        sort_label = ttk.Label(self.frame, text="Sort by:", style="BoldDark.TLabel")
        sort_label.grid(row=0, column=2, sticky="E")
        self.choices_sort_by = ['Proximity', 'Speed']
        self.sort_by = tk.StringVar()
        sort_box = ttk.OptionMenu(self.frame, self.sort_by, self.choices_sort_by[0], *self.choices_sort_by, command=self.sort_by_set, style="Dark.TMenubutton")
        sort_box.grid(row=0, column=3, sticky='W')
        self.sort_by.set(self.choices_sort_by[1])

        count_label = ttk.Label(self.frame, text="Objects:", style="BoldDark.TLabel")
        count_label.grid(row=0, column=4, sticky="E", ipadx=0, padx=0)
        


        t0_max_label = ttk.Label(self.frame, text="Primary", anchor='center', justify='center', style="Dark.TLabel")
        t0_max_label.grid(row=1, column=5, sticky="EW", ipadx=0, padx=0)

        t0_max_box = ttk.Entry(self.frame, textvariable=self.t0_max, justify='center', validate="focusout", validatecommand=self.t0_max_set, style="Dark.TEntry")
        t0_max_box.bind('<Return>', self.t0_max_set)
        t0_max_box.bind('<FocusIn>', self.highlight_t0)
        t0_max_box.bind('<Enter>', self.highlight_t0)
        t0_max_box.bind('<Leave>', self.highlight_t0)
        t0_max_box.grid(row=0, column=5, sticky='W', padx=(0,0))
        

        t1_max_label = ttk.Label(self.frame, text="Secondary", style="Dark.TLabel", anchor='center', justify='center')
        t1_max_label.grid(row=1, column=6, sticky="EW", ipadx=0, padx=(0,100))

        t1_max_box = ttk.Entry(self.frame, textvariable=self.t1_max, justify='center', validate="focusout", validatecommand=self.t1_max_set, style="Dark.TEntry")
        t1_max_box.bind('<Return>', self.t1_max_set)
        t1_max_box.bind('<FocusIn>', self.highlight_t1)
        t1_max_box.bind('<Enter>', self.highlight_t1)
        t1_max_box.bind('<Leave>', self.highlight_t1)

        t1_max_box.grid(row=0, column=6, sticky='WE', padx=(0,100))

        self.clock = ttk.Label(self.frame, text="00:00:00", anchor=tk.CENTER, style="Dark.TLabel")
        self.clock.grid(row=1, column=1)
        
        self.frame.columnconfigure((0,2,3,4),minsize=100, weight=0)
        self.frame.columnconfigure((1),minsize=103, weight=0)
        self.frame.columnconfigure((5,6),minsize=50, weight=1)

        self.frame.pack(padx=0, pady=(4,0),fill='both', expand=True)
        # self.frame.columnconfigure((5),minsize=50, weight=0)
        
        

        

        self.clock_update()

    def update(self, task):
        
        if task.subtype == 'toggle':
            value = task.data
            if value == 1: # start
                self.run_button.configure(style="Highlight.TButton", text='Stop')
            if value == 0: # stop
                self.run_button.configure(style="Dark.TButton", text='Start')

            # self.clock_label.configure(style="Highlight.TLabel")

        if task.subtype == 'sort_by':
            index = 0

            for i in range(len(self.choices_sort_by)):
                if self.config.properties.sort_by == self.choices_sort_by[i].upper():
                    index = i
                    
            self.sort_by.set(self.choices_sort_by[index])

        if task.subtype == 't0_max':
            try:
                val = int(self.config.properties.t0_max)
                self.t0_max.set(val)
            except ValueError:
                pass

        if task.subtype == 't1_max':
            try:
                val = int(self.config.properties.t1_max)
                self.t1_max.set(val)
            except ValueError:
                pass


    def clock_update(self):
        running_time = "00:00:00"
        style = "Dark.TLabel"
        if self.config and self.config.trajectories:
            if self.config.trajectories.simulating:
                time = self.config.time.time() - self.config.trajectories.time_0
                seconds = int(time % 60)
                minutes = int(time / 60) % 60
                hours = int(time / 3600) % 24
                running_time = "%s:%s:%s"%(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))#
                style = "Highlight.TLabel"

        self.clock.configure(text=running_time, style=style)

        self.clock.after(1000, self.clock_update)
            

    def sim_toggle(self):
        if self.config.trajectories:
            if not self.config.trajectories.simulating:
                self.config.simulation_start()
                if self.viewer:
                    if self.config.properties.auto_render == True:
                        self.viewer.rendering = True 
            else:
                self.config.simulation_stop()
                if self.viewer:
                    self.viewer.rendering = False


    def sort_by_set(self, event):
        self.config.properties.sort_by_set(self.sort_by.get().upper())
        

    def t0_max_set(self, event=None):
        update = self.config.properties.t0_max_set(self.t0_max.get())
        if update == False:
            self.t0_max.set(self.config.properties.t0_max)
        self.highlight_t0(event)

        
    def t1_max_set(self, event=None):
        update = self.config.properties.t1_max_set(self.t1_max.get())
        if update == False:
            self.t1_max.set(self.config.properties.t1_max)
        self.highlight_t1(event)
        

        


    def highlight_t0(self, event=None):
        if self.viewer:
            if event:
                # highlight mouse enter
                if event.type == '7': 
                    self.viewer.highlight_set(0, self.config.properties.t0_max, True)
                # highlight focus enter
                if event.type == '9': 
                    self.viewer.highlight_set(0, self.config.properties.t0_max, True)
                # highlight on keyboard event 
                if event.type == '2': 
                    self.viewer.highlight_set(0, self.config.properties.t0_max, True)
                # unhighlight mouse leave
                if event.type == '8': 
                    self.viewer.highlight_set(0, len(self.config.trajectories.satellites), False)
            
            # unhighlight focus leave
            else:
                self.viewer.highlight_set(0, len(self.config.trajectories.satellites), False)

        return True
    

    def highlight_t1(self, event=None):
        if event:
            if self.viewer:
                # highlight mouse enter
                if event.type == '7':
                    self.viewer.highlight_set(self.config.properties.t0_max, self.config.properties.t1_max, True)
                # highlight focus enter
                if event.type == '9':
                    self.viewer.highlight_set(self.config.properties.t0_max, self.config.properties.t1_max, True)
                # highlight focus enter
                if event.type == '2': 
                    self.viewer.highlight_set(self.config.properties.t0_max, self.config.properties.t1_max, True)
                # unhighlight mouse leave
                if event.type == '8':
                    self.viewer.highlight_set(0, len(self.config.trajectories.satellites), False)

            # unhighlight focus leave
            else:
                self.viewer.highlight_set(0, len(self.config.trajectories.satellites), False)

        return True
    

class AutomationBox(ttk.Frame):
    def __init__(self, root, config, viewer):
        self.root = root
        self.config = config
        self.viewer = viewer
        self.auto_save = tk.BooleanVar()
        self.auto_download = tk.BooleanVar()
        self.auto_simulate = tk.BooleanVar()
        self.auto_sleep = tk.BooleanVar()
        self.sleep_time = tk.StringVar()
        self.wake_time = tk.StringVar()
        self.auto_render = tk.BooleanVar()
        self.frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.frame.pack(padx=0, pady=(4,0), ipady=2, fill=tk.BOTH, expand=True)
        automation_label = ttk.Label(self.frame, text="Auto:", style="BoldDark.TLabel")
        automation_label.grid(row=0, column=0, sticky="E", padx=(0,4))

        auto_save_w = ttk.Checkbutton(self.frame,var=self.auto_save, command=self.auto_save_set, text="Save",style="Dark.TCheckbutton")
        self.auto_save.set(False)
        auto_save_w.grid(row=1, column=1, sticky="W")

        auto_download_w = ttk.Checkbutton(self.frame,var=self.auto_download, command=self.auto_download_set, text="Download", style="Dark.TCheckbutton")
        self.auto_download.set(False)
        auto_download_w.grid(row=1, column=2, sticky="W")

        automsim_w = ttk.Checkbutton(self.frame,var=self.auto_simulate, command=self.auto_simulate_set, text="Simulate",style="Dark.TCheckbutton")
        self.auto_simulate.set(False)
        automsim_w.grid(row=0, column=1, pady=(0,0), sticky="W")

        auto_render_w = ttk.Checkbutton(self.frame, var=self.auto_render, command=self.auto_render_set, text="Render",style="Dark.TCheckbutton")
        self.auto_render.set(False)
        auto_render_w.grid(row=1, column=5, sticky="W")
        self.choices_auto_render_range = ['In Range', 'Primary', 'Secondary', 'All']
        self.auto_render_range = tk.StringVar(self.root)
        self.auto_render_range.set(self.choices_auto_render_range[0])
        self.auto_render_range_box = ttk.OptionMenu(self.frame, self.auto_render_range, self.choices_auto_render_range[0], *self.choices_auto_render_range, command=self.auto_render_range_set, style="Dark.TMenubutton")
        self.auto_render_range_box.grid(row=2, column=5, sticky='W')
        self.auto_render_range_box.configure(state='disabled')

        self.render_step_label = ttk.Label(self.frame, text="Step", style="Dark.TLabel")
        self.render_step_label.grid(row=1, column=6, padx=(0,2), sticky='W')
        self.render_step_label.configure(state='disabled')

        self.choices_render_step = [0, 1, 2, 4, 8, 16, 24, 48]
        self.render_step = tk.IntVar(self.root)
        self.render_step.set(self.choices_render_step[0])
        self.render_step_box = ttk.OptionMenu(self.frame, self.render_step, self.choices_render_step[0], *self.choices_render_step, command=self.render_step_set, style="Dark.TMenubutton")
        self.render_step_box.grid(row=2, column=6, sticky='W')
        self.render_step_box.configure(state='disabled')




        self.choices_auto_save_interval = ['1 minute', '10 minutes', '30 minutes', '60 minutes', '90 minutes', '120 minutes']
        self.auto_save_interval = tk.StringVar(self.root)
        self.auto_save_interval.set(self.choices_auto_save_interval[1])
        self.auto_save_interval_box = ttk.OptionMenu(self.frame, self.auto_save_interval, self.choices_auto_save_interval[1], *self.choices_auto_save_interval, command=self.auto_save_interval_set, style="Dark.TMenubutton")
        self.auto_save_interval_box.grid(row=2, column=1, sticky='W')
        self.auto_save_interval_box.configure(state='disabled')

        self.choices_auto_download_interval = ['1 hour', '2 hours', '4 hours', '8 hours', '12 hours', '24 hours', '48 hours']
        self.auto_download_interval = tk.StringVar(self.root)
        self.auto_download_interval.set(self.choices_auto_download_interval[0])
        self.auto_download_interval_box = ttk.OptionMenu(self.frame, self.auto_download_interval, self.choices_auto_download_interval[0], *self.choices_auto_download_interval, command=self.auto_download_interval_set, style="Dark.TMenubutton")
        self.auto_download_interval_box.grid(row=2, column=2, sticky='W')
        self.auto_download_interval_box.configure(state='disabled')
        
        auto_sleep_w = ttk.Checkbutton(self.frame, var=self.auto_sleep, command=self.auto_sleep_set, text="Sleep",style="Dark.TCheckbutton")
        auto_sleep_w.grid(row=1, column=3, sticky="W")
        self.auto_sleep.set(False)

        self.until_label = ttk.Label(self.frame, text="Wake", style="Dark.TLabel")
        self.until_label.grid(row=1, column=4, sticky='W')

        self.sleep_time_entry = ttk.Entry(self.frame, textvariable=self.sleep_time, justify='center', validate="focusout", validatecommand=self.sleep_time_set, width=10, style="Dark.TEntry")
        self.sleep_time_entry.grid(row=2, column=3, sticky='EW')
        self.sleep_time.set("23:33")
        self.sleep_time_entry.configure(state='disabled')

        self.wake_time_entry = ttk.Entry(self.frame, textvariable=self.wake_time, justify='center', validate="focusout", validatecommand=self.wake_time_set, width=10, style="Dark.TEntry")
        self.wake_time_entry.grid(row=2, column=4, sticky='EW')
        self.wake_time.set("08:15")
        self.wake_time_entry.configure(state='disabled')


        self.sleep_time_entry.bind('<Return>', self.sleep_time_set)
        self.wake_time_entry.bind('<Return>', self.wake_time_set)


        self.frame.columnconfigure((0),minsize=100, weight=0)
        self.frame.columnconfigure((1,2,3,4,5),minsize=100, weight=0)

        # self.frame.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)

    def update(self, task, event=None):
        
        if task.subtype == 'auto_save':
            val = self.config.properties.auto_save
            if type(val) == bool:
                self.auto_save.set(val)
                if val == True:
                    self.auto_save_interval_box.configure(state='normal')
                else:
                    self.auto_save_interval_box.configure(state='disabled')


        if task.subtype == 'auto_save_interval':
            val = self.config.properties.auto_save_interval
            index = 0
            for i in range(len(self.choices_auto_save_interval)):
                if val == int(self.choices_auto_save_interval[i].split(" ")[0]):
                    index = i
            self.auto_save_interval.set(self.choices_auto_save_interval[index])
        
        if task.subtype == 'auto_download':
            val = self.config.properties.auto_download
            if type(val) == bool:
                self.auto_download.set(val)
                if val == True:
                    self.auto_download_interval_box.configure(state='normal')
                else:
                    self.auto_download_interval_box.configure(state='disabled')

        if task.subtype == 'auto_download_interval':
            val = self.config.properties.auto_download_interval
            index = 0
            for i in range(len(self.choices_auto_download_interval)):
                if val == int(self.choices_auto_download_interval[i].split(" ")[0]):
                    index = i
            self.auto_download_interval.set(self.choices_auto_download_interval[index])

        if task.subtype == 'auto_simulate':
            val = self.config.properties.auto_simulate
            if type(val) == bool:
                self.auto_simulate.set(val)

        if task.subtype == 'auto_render':
            val = self.config.properties.auto_render
            if type(val) == bool:
                self.auto_render.set(val)
                state = 'normal' if val == True else 'disabled'
                self.auto_render_range_box.configure(state=state)
                self.render_step_label.configure(state=state)
                self.render_step_box.configure(state=state)

        if task.subtype == 'auto_render_range':
            val = self.config.properties.auto_render_range
            index = 0
            for i in range(len(self.choices_auto_render_range)):
                if val == self.choices_auto_render_range[i]:
                    index = i
            self.auto_render_range.set(self.choices_auto_render_range[index])




        if task.subtype == 'auto_sleep':
            val = self.config.properties.auto_sleep
            if type(val) == bool:
                self.auto_sleep.set(val)
                if val == True:
                    self.sleep_time_entry.configure(state='normal')
                    self.wake_time_entry.configure(state='normal')
                else:
                    self.sleep_time_entry.configure(state='disabled')
                    self.wake_time_entry.configure(state='disabled')

        if task.subtype == 'auto_pin':
            val = self.config.properties.auto_pin
            if type(val) == bool:
                pass

        if task.subtype == 'sleep_time':         
            self.sleep_time.set(self.config.properties.sleep_time)

        if task.subtype == 'wake_time':
            self.wake_time.set(self.config.properties.wake_time)
            
        
    def auto_save_set(self, event=None):
        autosave = self.auto_save.get()
        self.config.properties.auto_save_set(autosave)
        if autosave == False:
            self.auto_save_interval_box.configure(state='disabled')
        else:
            self.auto_save_interval_box.configure(state='normal')


    def auto_save_interval_set(self, event=None):
        val = int(self.auto_save_interval.get().split(" ")[0])
        self.config.properties.auto_save_interval_set(val)
        
    def auto_download_set(self, event=None):
        autodownload = self.auto_download.get()
        self.config.properties.auto_download_set(autodownload)
        if autodownload == False:
            self.auto_download_interval_box.configure(state='disabled')
        else:
            self.auto_download_interval_box.configure(state='normal')




    def auto_download_interval_set(self, event=None):
        val = int(self.auto_download_interval.get().split(" ")[0])
        self.config.properties.auto_download_interval_set(val)
        
    def auto_simulate_set(self, event=None):
        self.config.properties.auto_simulate_set(self.auto_simulate.get())
        
    def auto_render_set(self, event=None):
        val = self.auto_render.get()
        self.config.properties.auto_render_set(val)
        if self.viewer:
            self.viewer.rendering = val
        state = 'normal'
        if val == False:
            state = 'disabled'

        self.auto_render_range_box.configure(state=state)
        self.render_step_label.configure(state=state)
        self.render_step_box.configure(state=state)
        
    def render_step_set(self, event=None):
        self.config.properties.render_step_set(self.render_step.get())

    def auto_sleep_set(self, event=None):
        autosleep = self.auto_sleep.get()
        self.config.properties.auto_sleep_set(autosleep)
        if autosleep == False:
            self.sleep_time_entry.configure(state='disabled')
            self.wake_time_entry.configure(state='disabled')
            self.until_label.configure(state='disabled')
        else:
            self.sleep_time_entry.configure(state='normal')
            self.wake_time_entry.configure(state='normal')
            self.until_label.configure(state='normal')

    def wake_time_set(self, event=None):
        wake_time = self.wake_time.get()
        update = False
        if wake_time != None:
            update = self.config.properties.wake_time_set(wake_time)
        if update == False:
            self.wake_time.set(self.config.properties.wake_time)
        else:
            self.wake_time.set(update) # correcting user input

    def sleep_time_set(self, event=None):
        sleep_time = self.sleep_time.get()
        update = False
        if sleep_time != None:
            update = self.config.properties.sleep_time_set(sleep_time)
        if update == False:
            self.sleep_time.set(self.config.properties.sleep_time)
        else:
            self.sleep_time.set(update) # correcting user input

    
    def auto_render_range_set(self, event=None):
        self.config.properties.auto_render_range_set(self.auto_render_range.get())
        self.config.trajectories.trim_render_queue()


class SatelliteBox(ttk.Frame):
    def __init__(self, root, config):
        self.root = root
        self.config = config
        frame = ttk.Frame(root, style="Dark.TFrame")
        frame.pack(padx=0, pady=(4,0), fill='both', expand=True)
        inrange_label = ttk.Label(frame, text="In Range:", style="BoldDark.TLabel")
        inrange_label.grid(row=0, column=0, sticky="NE", padx=(0,4))
        
        var = tk.Variable()
        self.inrange_list_ui = tk.Listbox(frame, listvariable=var, selectmode = tk.SINGLE, exportselection=False, width=28, height=12)
        self.inrange_list_ui.grid(row=0, column=1, columnspan=1, sticky='W')
        self.num_in_range = tk.Variable(value = 0)
        self.numinrange_label = ttk.Label(frame, text="0", width=2, style="BoldDark.TLabel")
        self.numinrange_label.grid(row=0, rowspan=1, column=2, sticky="SW", padx=(5,0), ipadx=0)

        frame.columnconfigure((0),minsize=100, weight=0)
        frame.columnconfigure((1),minsize=5, weight=0)
        frame.columnconfigure((2),minsize=0, weight=0)
        frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT, padx=0, pady=5) 

    def update(self):
        if self.config and self.config.trajectories:
            if len(self.config.trajectories.in_range) == 0:
                self.inrange_list_ui.delete(0, tk.END)
            else:
                new = [j for j in self.config.trajectories.in_range if j not in self.inrange_list_ui.get(0, tk.END)]
                
                for i, item in enumerate(self.inrange_list_ui.get(0, tk.END)):
                    if item not in self.config.trajectories.in_range:
                        self.inrange_list_ui.delete(i)
                
                for i in range(len(new)):
                    self.inrange_list_ui.insert(tk.END, new[i])

                self.inrange_list_ui.configure(fg='grey50')
            
            self.numinrange_label.configure(text=len(self.config.trajectories.in_range))
        

class OutputBox(ttk.Frame):
    def __init__(self, root, config):
        self.root = root
        self.config = config

        self.auto_pin = tk.BooleanVar()
        
        self.pin_0_use = tk.BooleanVar()
        self.pin_0 = tk.IntVar()
        self.pin_0_value = tk.StringVar()
        self.pin_0_condition = tk.StringVar()
        
        self.pin_1_use = tk.BooleanVar()
        self.pin_1 = tk.IntVar()
        self.pin_1_value = tk.StringVar()
        self.pin_1_condition = tk.StringVar()


        self.pin_baud = tk.IntVar()
        self.pin_port = tk.StringVar()

        self.auto_serial = tk.BooleanVar()
        self.serial_port = tk.StringVar()
        self.serial_baud = tk.StringVar()
        self.serial_value = tk.StringVar()
        self.serial_ignore = tk.StringVar()

        self.auto_log = tk.BooleanVar()
        self.log_engine = tk.BooleanVar()
        self.log_num_in_range = tk.BooleanVar()
        self.log_in_range = tk.BooleanVar()
        self.log_none_in_range = tk.BooleanVar()

        self.log_file = tk.StringVar()


         
        tabsystem = ttk.Notebook(root, style="Dark.TNotebook")
        
        ################################ Label Tab ################################
        label_tab = ttk.Frame(tabsystem, style="Dark.TNotebook.Tab")
        tabsystem.add(label_tab, text="Output:", state="disabled")

        ################################ Pin Tab ################################
        self.choices_pin = [i for i in reversed(range(26))]
        self.choices_pin_state = ['High', 'Low']
        self.choices_pin_value = ['Satellites in Range', 'No Satellites in Range', 'Sleeping', 'Not Sleeping']
        pin_tab = ttk.Frame(tabsystem, style="Dark.TNotebook.Tab")
        
        #### Pin 0 Row 0 ####
        pin_0_row_0 = ttk.Frame(pin_tab, style="Dark.TNotebook.Tab")
        pin_0_label = ttk.Checkbutton(pin_0_row_0, var=self.pin_0_use, command=self.pin_0_use_set, text="Pin",style="Dark.TCheckbutton")
        self.pin_0_use.set(False)
        pin_0_label.grid(row=0, column=0, sticky="E", padx=(0,2), pady=0)
        self.pin_0_box = ttk.OptionMenu(pin_0_row_0, self.pin_0, self.choices_pin[-1], *self.choices_pin, command=self.pin_0_set, direction='above', style="Dark.TMenubutton")
        self.pin_0_box.configure(state='disabled')
        self.pin_0_box.grid(row=0, column=1, padx=0, ipadx=0)
        
        self.pin_0_value_box = ttk.OptionMenu(pin_0_row_0, self.pin_0_value, self.choices_pin_state[0], *self.choices_pin_state, command=self.pin_0_value_set, style="Dark.TMenubutton")
        self.pin_0_value_box.configure(state='disabled')
        self.pin_0_value_box.grid(row=0, column=2, padx=0, ipadx=0)
        pin_0_row_0.columnconfigure((0,1,2), minsize=50, weight=0)
        pin_0_row_0.pack(padx=20, pady=(20,0), anchor='nw')



        #### Pin 0 Row 1 ####
        pin_0_row_1 = ttk.Frame(pin_tab, style="Dark.TNotebook.Tab")
        pin_0_condition_label = ttk.Label(pin_0_row_1, text="If", style="Dark.TLabel")
        pin_0_condition_label.grid(row=1, column=0, sticky="E", padx=(0,2))

        self.pin_0_condition_box = ttk.OptionMenu(pin_0_row_1, self.pin_0_condition, self.choices_pin_value[0], *self.choices_pin_value, command=self.pin_0_condition_set, style="DarkFixed.TMenubutton")
        self.pin_0_condition_box.grid(row=1, column=1, sticky='W', padx=0, ipadx=0)
        self.pin_0_condition_box.configure(state='disabled')
        pin_0_row_1.columnconfigure((0), minsize=50, weight=0)
        
        pin_0_row_2 = ttk.Frame(pin_tab, style="Dark.TNotebook.Tab")
        
        
        pin_0_display_label = ttk.Label(pin_0_row_1, text="State", justify='center', width=5, style="Dark.TLabel")
        pin_0_display_label.grid(row=2, column=0, padx=(0,2), sticky='E')
        self.pin_0_display = ttk.Label(pin_0_row_1, text="", justify='center', width=5, style="Highlight.TLabel")
        self.pin_0_display.grid(row=2, column=1, sticky='W')
        self.pin_0_display.configure(text="None", state='disabled')
        pin_0_row_1.pack(padx=20, pady=(0,0), anchor='nw')



        #### Pin 1 Row 0 ####
        pin_1_row_0 = ttk.Frame(pin_tab, style="Dark.TNotebook.Tab")
        pin_1_label = ttk.Checkbutton(pin_1_row_0, var=self.pin_1_use, command=self.pin_1_use_set, text="Pin",style="Dark.TCheckbutton")
        self.pin_1_use.set(False)
        pin_1_label.grid(row=0, column=0, sticky="E", padx=(0,2), pady=0)

        self.pin_1_box = ttk.OptionMenu(pin_1_row_0, self.pin_1, self.choices_pin[-2], *self.choices_pin, command=self.pin_1_set, direction='above', style="Dark.TMenubutton")
        self.pin_1_box.grid(row=0, column=1, padx=0, ipadx=0)
        self.pin_1_box.configure(state='disabled')

        self.pin_1_value_box = ttk.OptionMenu(pin_1_row_0, self.pin_1_value, self.choices_pin_state[1], *self.choices_pin_state, command=self.pin_1_value_set, style="Dark.TMenubutton")
        self.pin_1_value_box.grid(row=0, column=2, padx=0, ipadx=0)
        self.pin_1_value_box.configure(state='disabled')
        pin_1_row_0.columnconfigure((0,1,2), minsize=50, weight=0)
        pin_1_row_0.pack(padx=20, pady=(20,0), anchor='nw')

        #### Pin 1 Row 1 ####
        pin_1_row_1 = ttk.Frame(pin_tab, style="Dark.TNotebook.Tab")
        pin_1_condition_label = ttk.Label(pin_1_row_1, text="If", style="Dark.TLabel")
        pin_1_condition_label.grid(row=1, column=0, sticky="E", padx=(0,2))

        self.pin_1_condition_box = ttk.OptionMenu(pin_1_row_1, self.pin_1_condition, self.choices_pin_value[2], *self.choices_pin_value, command=self.pin_1_condition_set, style="DarkFixed.TMenubutton")
        self.pin_1_condition_box.grid(row=1, column=1, sticky='W', padx=0, ipadx=0)
        self.pin_1_condition_box.configure(state='disabled')

        pin_1_display_label = ttk.Label(pin_1_row_1, text="State", justify='center', width=5, style="Dark.TLabel")
        pin_1_display_label.grid(row=2, column=0, padx=(0,2), sticky='E')

        self.pin_1_display = ttk.Label(pin_1_row_1, text="", justify='center', width=5, style="Highlight.TLabel")
        self.pin_1_display.grid(row=2, column=1, sticky='W')
        self.pin_1_display.configure(text="None", state='disabled')
        
        pin_1_row_1.columnconfigure((0), minsize=50, weight=0)
        pin_1_row_1.pack(padx=20, pady=(0,0), anchor='nw')






        tabsystem.add(pin_tab, text="Pin")

        ################################ Serial Tab ################################
        serial_tab = ttk.Frame(tabsystem, style="Dark.TNotebook.Tab")
        serial_frame = ttk.Frame(serial_tab, style="Dark.TNotebook.Tab")
        
        serial_port_use_label = ttk.Label(serial_frame, text="Use:", style="Dark.TLabel")  
        serial_port_use_label.grid(row=0, column=0, sticky="E", padx=0, pady=0)
        serial_port_use = ttk.Checkbutton(serial_frame, var=self.auto_serial, command=self.auto_serial_set, text="", style="Dark.TCheckbutton")
        serial_port_use.grid(row=0, column=1, columnspan=2, sticky="E", padx=0, pady=0)

        serial_port_label = ttk.Label(serial_frame, text="Port:", style="Dark.TLabel")
        serial_port_label.grid(row=1, column=0, sticky="E", padx=0, pady=0)
        self.serial_port = tk.StringVar()
        self.serial_port_input = ttk.Entry(serial_frame, textvariable=self.serial_port, validate='focusout', validatecommand=self.serial_port_set, style="Dark.TEntry")
        self.serial_port_input.bind('<Return>', self.serial_port_set)
        self.serial_port_input.grid(row=1, column=1, columnspan=2, padx=0, sticky='EW')

        serial_baud_label = ttk.Label(serial_frame, text="Baud:", style="Dark.TLabel")
        serial_baud_label.grid(row=2, column=0, sticky="E")
        self.serial_baud_input = ttk.Entry(serial_frame, textvariable=self.serial_baud, validate='focusout', validatecommand=self.serial_baud_set, style="Dark.TEntry")
        self.serial_baud_input.bind('<Return>', self.serial_baud_set)
        self.serial_baud_input.grid(row=2, column=1, columnspan=2, sticky='EW')

        serial_value_label = ttk.Label(serial_frame, text="Value:", style="Dark.TLabel")
        serial_value_label.grid(row=3, column=0, sticky="E")
        
        self.choices_serial_value = ['In Range Count', 'Satellites in Range', 'No Satellites in Range']
        self.serial_value = tk.StringVar()
        serial_value_box = ttk.OptionMenu(serial_frame, self.serial_value, self.choices_serial_value[0], *self.choices_serial_value, command=self.serial_value_set, style="DarkFixed.TMenubutton")
        serial_value_box.grid(row=3, column=1, columnspan=2, sticky='EW')

        serial_frame.columnconfigure((0,1), minsize=20, weight=1)
        serial_frame.pack(padx=20, pady=20, anchor='nw')
        tabsystem.add(serial_tab, text="Serial")
        
        ################################ Log Tab ################################
        log_tab = ttk.Frame(tabsystem, style="Dark.TNotebook.Tab")
        log_frame = ttk.Frame(log_tab, style="Dark.TNotebook.Tab")
                
        log_use = ttk.Checkbutton(log_frame, var=self.auto_log, command=self.auto_log_set, text="Use", style="Dark.TCheckbutton")
        log_use.grid(row=0, column=0, columnspan=2, sticky="W", padx=0, pady=0)
        
        log_engine = ttk.Checkbutton(log_frame, var=self.log_engine, command=self.log_engine_set, text="Engine", style="Dark.TCheckbutton")
        log_engine.grid(row=1, column=0, columnspan=2, sticky="W", padx=0, pady=0)
        
        log_in_range = ttk.Checkbutton(log_frame, var=self.log_in_range, command=self.log_in_range_set, text="In Range", style="Dark.TCheckbutton")
        log_in_range.grid(row=2, column=0, columnspan=2, sticky="W", padx=0, pady=0)

        log_num_in_range = ttk.Checkbutton(log_frame, var=self.log_num_in_range, command=self.log_num_in_range_set, text="Number In Range", style="Dark.TCheckbutton")
        
        log_num_in_range.grid(row=3, column=0, columnspan=2, sticky="W", padx=0, pady=0)

        # log_file_label = ttk.Label(log_frame, text="File:", style="Dark.TLabel")  
        # log_file_label.grid(row=4, column=0, sticky="W", padx=0, pady=0)


        self.log_file_open_button = ttk.Button(log_frame, text="Open", command=self.log_file_open, style="Dark.TButton")
        self.log_file_open_button.grid(row=4, column=0, columnspan=4, sticky='EW', padx=0)


        log_frame.columnconfigure((0,1,2), minsize=20, weight=1)

        log_frame.pack(padx=20, pady=20, anchor='w')
        tabsystem.add(log_tab, text="Log")



        tabsystem.pack(expand=1, fill=tk.BOTH, padx=(0,100), pady=5)
        root.pack(padx=(0,0), ipadx=0, pady=(4,4), expand=1, fill=tk.BOTH)

    def update(self, task):
        if task.subtype == 'auto_serial':
            self.auto_serial.set(self.config.properties.auto_serial)
        if task.subtype == 'serial_port':
            self.serial_port.set(self.config.properties.serial_port)
        if task.subtype == 'serial_baud':
            self.serial_baud.set(self.config.properties.serial_baud)
        if task.subtype == 'serial_value':
            index = 0
            for i in range(len(self.choices_serial_value)):
                if self.config.properties.serial_value == self.choices_serial_value[i]:
                    index = i
                    
            self.serial_value.set(self.choices_serial_value[index])


        if task.subtype == 'pin_0_use':
            pin_use = self.config.properties.pin_0_use
            self.pin_0_use.set(pin_use)
            state = 'normal' if pin_use == True else 'disabled'
            self.box_state_set([self.pin_0_box, self.pin_0_value_box, self.pin_0_condition_box, self.pin_0_display], state)

        if task.subtype == 'pin_0':
            self.pin_0.set(self.config.properties.pin_0)

        if task.subtype == 'pin_0_value':
            self.pin_0_value.set(self.config.properties.pin_0_value)

        if task.subtype == 'pin_0_condition':
            self.pin_0_condition.set(self.config.properties.pin_0_condition)

        if task.subtype == 'pin_0_state':
            val = self.config.properties.pin_0_state
            txt = "HIGH" if val == True else "LOW"
            self.pin_0_display.configure(text=txt)

        if task.subtype == 'pin_1_use':
            pin_use = self.config.properties.pin_1_use
            self.pin_1_use.set(pin_use)
            state = 'normal' if pin_use == True else 'disabled'
            self.box_state_set([self.pin_1_box, self.pin_1_value_box, self.pin_1_condition_box, self.pin_1_display], state)
            
           
        if task.subtype == 'pin_1':
            self.pin_1.set(self.config.properties.pin_1)

        if task.subtype == 'pin_1_value':
            self.pin_1_value.set(self.config.properties.pin_1_value)

        if task.subtype == 'pin_1_condition':
            self.pin_1_condition.set(self.config.properties.pin_1_condition)

        if task.subtype == 'pin_1_state':
            val = self.config.properties.pin_1_state
            txt = "HIGH" if val == True else "LOW"
            self.pin_1_display.configure(text=txt)

    def pin_0_use_set(self, event=None):
        pin_use = self.pin_0_use.get()
        if pin_use == True:
            state = 'normal'
        else:
            state = 'disabled'
        self.box_state_set([self.pin_0_box, self.pin_0_value_box, self.pin_0_condition_box, self.pin_0_display], state)
        self.config.properties.pin_0_use_set(pin_use)

    def box_state_set(self, boxes, state):
        if type(boxes) != list:
            boxes = [boxes]
        for box in boxes:
            box.configure(state=state)


    def pin_1_use_set(self, event=None):
        pin_use = self.pin_1_use.get()
        if pin_use == True:
            state = 'normal'
        else:
            state = 'disabled'
        self.box_state_set([self.pin_1_box, self.pin_1_value_box, self.pin_1_condition_box, self.pin_1_display], state)
        self.config.properties.pin_1_use_set(pin_use)

    def pin_0_set(self, event=None):
        pin = self.pin_0.get()
        self.config.properties.pin_0_set(pin)

    def pin_0_value_set(self, event=None):
        state = self.pin_0_value.get()
        self.config.properties.pin_0_value_set(state)

    def pin_0_condition_set(self, event=None):
        value = self.pin_0_condition.get()
        self.config.properties.pin_0_condition_set(value)
    
    def pin_1_set(self, event=None):
        pin = self.pin_1.get()
        self.config.properties.pin_1_set(pin)

    def pin_1_value_set(self, event=None):
        state = self.pin_1_value.get()
        self.config.properties.pin_1_value_set(state)

    def pin_1_condition_set(self, event=None):
        value = self.pin_1_condition.get()
        self.config.properties.pin_1_condition_set(value)


    def auto_serial_set(self, event=None):
        if self.config and self.config.properties:
            self.config.properties.auto_serial_set(self.auto_serial.get())

    def serial_port_set(self, event=None):
        if self.config and self.config.properties:
            self.config.properties.serial_port_set(self.serial_port.get())

    def serial_baud_set(self, event=None):
        if self.config and self.config.properties:
            self.config.properties.serial_baud_set(self.serial_baud.get())

    def serial_value_set(self, event=None):
        if self.config and self.config.properties:
            self.config.properties.serial_value_set(self.serial_value.get())

    def serial_ignore_set(self, event=None):
        pass

    def auto_log_set(self, event=None):
        pass

    def log_engine_set(self, event=None):
        pass

    def log_num_in_range_set(self, event=None):
        pass

    def log_in_range_set(self, event=None):
        pass
    
    def log_none_in_range_set(self, event=None):
        pass

    def log_file_open(self, event=None):
        pass


class Viewer(ttk.Frame):
    def __init__(self, parent, config, title, resizable, geometry, background, *args, **kwargs):
        self.config = config
        self.root = tk.Toplevel()
        self.parent = parent
        self.root.title(title)
        self.root.resizable(resizable[0], resizable[1])
        res_x = RESOLUTION_X
        res_y = RESOLUTION_Y
        self.objects = []
        
        self.render_thread = None
        self.rendering = False
        self.render_once = False

        if geometry:
            self.root.geometry(geometry)
            g = geometry.replace('x',' ').replace('+', ' ').split(' ')
            if len(g) == 4:
                x, y = g[0], g[1]
                try:
                    res_x = int(x)
                    res_y = int(y)
                except TypeError:
                    pass

        self.canvas = tk.Canvas(self.root, width=res_x, height=res_y)

        if background == 'DEFAULT': 
            scriptdir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
            asset_dir = os.path.join(scriptdir.parent.absolute(), "assets")
            mercator = os.path.isfile(os.path.join(asset_dir, "mercator.png"))
            
            if mercator:
                self.background_set(os.path.join(asset_dir, "mercator.png"))
            
        self.update()
        current_time = time.strftime("%H:%M:%S")
        msg = "%s Viewer initialized"%current_time
        print(msg)
        self.config.log(msg)

        if self.config.properties.auto_simulate and self.config.properties.auto_render:
            self.rendering = True 

        
    def background_set(self, path):
        self.background_image = tk.PhotoImage(file=path)
        img = self.canvas.create_image(0,0, image=self.background_image, anchor=tk.NW)
        self.canvas.tag_lower(img)
        self.canvas.pack(anchor=tk.CENTER, expand=True)


    def update_inrange_colors(self):
        if self.config and self.config.trajectories:
            for obj in self.config.trajectories.satellites:
                if obj.render_obj and obj.render_obj in self.objects:
                    fill = 'black'
                    outline = 'black'
                    if obj.in_range:
                        fill = 'red'
                    else:
                        fill = 'grey'
                        if obj.distance_2D:
                            fill += str(min(int(obj.distance_2D/20000 * 100),100))
                    if obj.highlight:
                        outline = 'yellow'
                        
                    self.canvas.itemconfig(obj.render_obj, state='normal', fill=fill, outline=outline)

        return True            

        
    def render_satellite(self):
        obj = self.config.trajectories.render_queue.get()
        if not self.config.properties.auto_render:
            self.config.trajectories.render_queue.task_done()

        else:
            obj_radius = 16
            if obj.pixel_x and obj.pixel_y:
                if not obj.render:
                    if obj.render_obj:
                        self.canvas.itemconfigure(obj.render_obj, state='hidden')
                
                else:
                    outline = 'black'
                    if obj.highlight:
                        outline = 'yellow'

                    fill = "grey" 
                    if obj.in_range:
                        fill = 'red'
                    else:
                        if obj.distance_2D:
                            fill += str(min(int(obj.distance_2D/20000 * 100),100))

                    if obj.render_obj and obj.render_obj in self.objects: 
                        self.canvas.itemconfig(obj.render_obj, 
                                            state='normal', 
                                            fill=fill,
                                            outline=outline
                                            )  
                       
                        self.canvas.moveto(obj.render_obj, obj.pixel_x, obj.pixel_y)
                        
                    else:
                        x1 = obj.pixel_x + (obj_radius / 2)
                        x2 = x1 + obj_radius
                        y1 = obj.pixel_y - (obj_radius / 2)
                        y2 = y1 + obj_radius
                        
                        obj.render_obj = self.canvas.create_arc(x1, 
                                                                y1, 
                                                                x2, 
                                                                y2, 
                                                                start=100, 
                                                                extent=45, 
                                                                fill=fill, 
                                                                outline=outline,
                                                                offset='center'
                                                                )
                        # obj.color = col
                        self.objects.append(obj.render_obj)
            self.config.trajectories.render_queue.task_done()
            


    def render_objects_reset(self):
        for i in range(len(self.objects)):
            obj = self.objects[i]
            self.canvas.delete(obj)
        self.objects = []


    def highlight_set(self, indexmin, indexmax, value=None):
        if type(indexmin) == int and type(indexmax) == int:
            indexmin = max(0, indexmin)
            if self.config.trajectories.satellites:

                indexmax = min(indexmax, len(self.config.trajectories.satellites))
                
                for i in range(len(self.config.trajectories.satellites)):
                    sat = self.config.trajectories.satellites[i]

                    if i >= indexmin and i < indexmax:
                        sat.highlight = value

                    else:
                        sat.highlight = False

                    if sat.render and sat.render_obj:
                        outline = 'black'
                        if sat.highlight:
                            outline = 'yellow'
                        self.canvas.itemconfig(sat.render_obj, outline=outline)
                        if sat.highlight:
                            self.canvas.tag_raise(sat.render_obj)    
            
                  

    def update(self):
        if self.rendering == True:
            render_step = 1000
            # print(self.config.trajectories.render_queue.qsize())
            if self.config and self.config.trajectories and self.config.trajectories.render_queue:
                for i in range(render_step):
                    if self.rendering == False:
                        break
                    if not self.config.trajectories.render_queue.empty():
                        self.render_satellite()
                        

        
        if self.render_once == True:
            self.config.trajectories.trim_render_queue()
            while not self.config.trajectories.render_queue.empty():
                self.render_satellite()
            self.render_once = False
           

        self.root.after(1, self.update)


    def update_once(self):
        self.config.trajectories.reset_render_queue(repopulate=True)
        self.update_inrange_colors()
        self.render_once = True
        

    def clear(self):
        for o in self.objects:
            self.canvas.delete(o)


class Gui(ttk.Frame):
    def __init__(self, 
                 config, 
                 title_main, 
                 title_viewer, 
                 resizable_main, 
                 resizable_viewer, 
                 geometry_main, 
                 geometry_viewer, 
                 background_viewer, 
                 *args, 
                 **kwargs):
        self.config = config
        
        root = tk.Tk()
        root.geometry(geometry_main)
        root.title(title_main)
        root.resizable(resizable_main[0], resizable_main[1])
        self.root = root
        # root.configure(background='#2C2C2C')
        self.style = strwueuestyle()

        self.viewer = Viewer(self.root, config, title_viewer, resizable_viewer, geometry_viewer, background_viewer, *args, **kwargs)
        self.location_box = LocationBox(root, config)
        self.selection_box = SelectionBox(root, config)
        self.file_box = FileBox(root, config)
        self.option_box = OptionBox(root, config)
        self.simulation_box = SimulationBox(root, config, self.viewer)
        self.automation_box = AutomationBox(root, config, self.viewer)
        
        self.satcom_box = ttk.Frame(root, style="Dark.TFrame")
        self.satellite_box = SatelliteBox(self.satcom_box, config)
        self.output_box = OutputBox(self.satcom_box, config)

        root.bind('<F12>', self.config.toggle_sleep)


        self.task_map = {
            "loc_query": "LOCATION_UPDATE",
            "loc_list": "LOCATION_UPDATE",

            "lat": "SELECTION_UPDATE",
            "lon": "SELECTION_UPDATE",
            "timezone": "SELECTION_UPDATE",
            "loc_index": "SELECTION_UPDATE",
            
            "sessiondata_file": "FILE_UPDATE",
            "config_file": "FILE_UPDATE",
            "tle_file": "FILE_UPDATE",
            "saved": "FILE_UPDATE",

            "sim_age": "FILE_UPDATE",
            
            "radius": "OPTION_UPDATE",
            "classification": "OPTION_UPDATE",
            "filter": "OPTION_UPDATE",
            
            "t0_max": "SIMULATION",
            "t1_max": "SIMULATION",
            "sort_by": "SIMULATION",
            
            "serial_port": "OUTPUT_UPDATE",
            "serial_baud": "OUTPUT_UPDATE",
            "serial_value": "OUTPUT_UPDATE",
            "auto_serial": "OUTPUT_UPDATE",
            
            "auto_save": "AUTOMATION_UPDATE",
            "auto_save_interval": "AUTOMATION_UPDATE",
            "auto_download": "AUTOMATION_UPDATE",
            "auto_download_interval": "AUTOMATION_UPDATE",
            "auto_simulate": "AUTOMATION_UPDATE",
            "auto_sleep": "AUTOMATION_UPDATE",
            "auto_pin": "AUTOMATION_UPDATE",
            "auto_render": "AUTOMATION_UPDATE",
            "auto_render_range": "AUTOMATION_UPDATE",
            "wake_time": "AUTOMATION_UPDATE",
            "sleep_time": "AUTOMATION_UPDATE",


            "viewer": "VIEWER_UPDATE",

            "pin_0_use": "OUTPUT_UPDATE",
            "pin_0": "OUTPUT_UPDATE",
            "pin_0_value": "OUTPUT_UPDATE",
            "pin_0_condition": "OUTPUT_UPDATE",
            "pin_0_state": "OUTPUT_UPDATE",

            "pin_1_use": "OUTPUT_UPDATE",
            "pin_1": "OUTPUT_UPDATE",
            "pin_1_value": "OUTPUT_UPDATE",
            "pin_1_condition": "OUTPUT_UPDATE",
            "pin_1_state": "OUTPUT_UPDATE",

            
        
        
        
        }

        self.update()
    
    def update(self):
        while not self.config.ui_q.empty():
            task = self.config.ui_q.get()
            # TODO: streamline
            if task.type == 'UI_UPDATE' and task.subtype in self.task_map:
                task.type = self.task_map[task.subtype]

            if task.type == 'VIEWER_UPDATE':
                if self.viewer:
                    self.viewer.update_once()

            if task.type == 'LOCATION_UPDATE':
                self.location_box.update(task)

            if task.type == 'SELECTION_UPDATE':
                self.selection_box.update(task)

            if task.type == 'FILE_UPDATE':
                self.file_box.update(task)
            ### Info Line located in file box
            if task.type == 'INFO_UPDATE':
                self.file_box.update(task)

            if task.type == 'OPTION_UPDATE':
                self.option_box.update(task)

            if task.type == 'SIMULATION':
                if task.subtype == 'sort_by':
                    self.simulation_box.update(task)
                    
                elif task.subtype == 't0_max' or task.subtype == 't1_max':
                    self.simulation_box.update(task)

                elif task.subtype == 'toggle':
                    self.simulation_box.update(task)


                else: # subtypes: classification, filter, radius
                    self.satellite_box.update()
                    
            if task.type == 'IO':
                if task.subtype == 'sleep':
                    self.selection_box.update(task)
                    self.output_box.update(task)

                elif task.subtype == 'in_range_list':
                    self.satellite_box.update()

                elif task.subtype == None:
                    self.output_box.update(task)
                pass

            if task.type == 'RENDERING':
                if task.subtype == 'reset':
                    self.viewer.render_objects_reset()


            if task.type == 'AUTOMATION_UPDATE':
                self.automation_box.update(task)

            if task.type == 'SATELLITE_UPDATE':
                self.satellite_box.update(task)

            if task.type == 'OUTPUT_UPDATE':
                self.output_box.update(task)

            self.config.ui_q.task_done()

        self.root.after(100, self.update)
