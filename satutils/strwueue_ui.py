#!/home/schnollie/.venvs/strwueue/bin/python
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from strwueue_style import style as strwueuestyle
from strwueue_utils import location_query
from strwueue_engine import Engine

class Ui(ttk.Frame):
    def __init__(self, parent, engine, trajectories = None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        self.style = strwueuestyle()

        self.engine = engine
        self.trajectories = trajectories
        self.location = tk.StringVar()
        self.config_val = None
        self.tle_val = None
        self.trajectories_val = None
        self.loc_list = []
        self.sim_running = False

        ############################################ Location Box ############################################
        ######################################################################################################
        self.locations_box = ttk.Frame(self.parent)
        self.locations_box.pack(padx=0, pady=2, fill='both', expand=True)

        location_label = ttk.Label(self.locations_box, text="Location:")
        location_entry = ttk.Entry(self.locations_box, textvariable=self.location)
        location_entry.bind('<Return>', self.location_submit)

        location_button = ttk.Button(self.locations_box, text="OK", command=self.location_submit)
        self.loc_list_ui = tk.Listbox(self.locations_box, selectmode = tk.BROWSE, width=66)
        self.loc_list_ui.bind('<<ListboxSelect>>', self.location_select)
        self.loc_list_ui.bind('<Return>', self.location_select)

        location_label.grid(row=0, column=0, columnspan=1)
        location_entry.grid(row=0, column=1, columnspan=5, padx=2, pady=2, sticky="EW")
        location_button.grid(row=0, column=6, padx=2, pady=2)
        self.loc_list_ui.grid(row=1, column=1, columnspan=6, rowspan=8, padx=2, pady=2, sticky='EW')
        self.locations_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=0)

        ############################################ Selection Box ############################################
        #######################################################################################################
        selection_box = ttk.Frame(self.parent)
        selection_box.pack(padx=0, pady=2, fill='both', expand=True)

        select_label = ttk.Label(selection_box, text="Selection:")
        self.select_val = ttk.Label(selection_box, text="")

        address_label = ttk.Label(selection_box, text="Address:")
        self.address_val = ttk.Label(selection_box, text="")

        zip_label = ttk.Label(selection_box, text="Zip Code:")
        self.zip_val = ttk.Label(selection_box, text="")

        city_label = ttk.Label(selection_box, text="City:")
        self.city_val = ttk.Label(selection_box, text="")


        district_label = ttk.Label(selection_box, text="District:")
        self.district_val = ttk.Label(selection_box, text="")

        country_label = ttk.Label(selection_box, text="Country:")
        self.country_val = ttk.Label(selection_box, text="")

        lat_label = ttk.Label(selection_box, text="Latitude:")
        self.lat_val = ttk.Label(selection_box, text="")

        lon_label = ttk.Label(selection_box, text="Longitude:")
        self.lon_val = ttk.Label(selection_box, text="")

        select_label.grid(row=0, column=0, columnspan=1, sticky="E")
        self.select_val.grid(row=0, column=1, sticky="W")

        address_label.grid(row=1, column=0, columnspan=1, sticky="E")
        self.address_val.grid(row=1, column=1, sticky="W")

        zip_label.grid(row=2, column=0, columnspan=1, sticky="E")
        self.zip_val.grid(row=2, column=1, sticky="W")

        city_label.grid(row=3, column=0, columnspan=1, sticky="E")
        self.city_val.grid(row=3, column=1, sticky="W")

        district_label.grid(row=4, column=0, columnspan=1, sticky="E")
        self.district_val.grid(row=4, column=1, sticky="W")

        country_label.grid(row=5, column=0, columnspan=1, sticky="E")
        self.country_val.grid(row=5, column=1, sticky="W")

        lat_label.grid(row=6, column=0, columnspan=1, sticky="E")
        self.lat_val.grid(row=6, column=1, sticky="W")

        lon_label.grid(row=7, column=0, columnspan=1, sticky="E")
        self.lon_val.grid(row=7, column=1, sticky="W")

        selection_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=0)


        ############################################ File Box ############################################
        ##################################################################################################
        file_box = ttk.Frame(self.parent)
        file_box.pack(padx=0, pady=2, fill='both', expand=True)
        config_row = 0
        tle_row = 1
        trajectory_row = 2
        radius_step_row = 3
        info_row_0 = 4
        info_row_1 = 5
        info_row_2 = 6
        info_row_3 = 7
        info_row_4 = 8


        ################################ CONFIG ################################
        config_label = ttk.Label(file_box, text="Config:").grid(row=config_row, column=0, columnspan=1, sticky="E")
        self.config_open_button = ttk.Button(file_box, text="Open", command=self.config_open)
        self.config_open_button.grid(row=config_row, column=1, sticky='EW', padx=0)

        get_config_button = ttk.Button(file_box, text="New", command=self.config_new)
        get_config_button.grid(row=config_row, column=2, sticky='WE', padx=0)

        save_config_button = ttk.Button(file_box, text="Save", command=self.config_save)
        save_config_button.grid(row=config_row, column=3, sticky='W', padx=0)

        ################################ TLE ################################
        tle_label = ttk.Label(file_box, text="TLEs:").grid(row=tle_row, column=0, columnspan=1, sticky="E")
        self.tle_open_button = ttk.Button(file_box, text="Open", command=self.tle_open)
        self.tle_open_button.grid(row=tle_row, column=1, sticky='EW', padx=0)

        get_tle_button = ttk.Button(file_box, text="New", command=self.tle_new)
        get_tle_button.grid(row=tle_row, column=2, sticky='WE', padx=0)

        save_tle_button = ttk.Button(file_box, text="Save", command=self.tle_save)
        save_tle_button.grid(row=tle_row, column=3, sticky='W', padx=0)

        ################################ TRAJECTORIES ################################
        trajectories_label = ttk.Label(file_box, text="Trajectories:")
        trajectories_label.grid(row=trajectory_row, column=0, columnspan=1, sticky="E")

        self.trajectories_open_button = ttk.Button(file_box, text="Open", command=self.trajectories_open)
        self.trajectories_open_button.grid(row=trajectory_row, column=1, sticky='EW', padx=0)

        get_trajectories_button = ttk.Button(file_box, text="New", command=self.trajectories_new)
        get_trajectories_button.grid(row=trajectory_row, column=2, sticky='WE', padx=0)

        save_trajectories_button = ttk.Button(file_box, text="Save", command=self.trajectories_save)
        save_trajectories_button.grid(row=trajectory_row, column=3, sticky='W', padx=0)

        file_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)

        ################################ INFO ################################ 
        info_0_label = ttk.Label(file_box, text="Info:")
        info_0_label.grid(row=info_row_0, column=0, columnspan=1, rowspan=1, sticky="E")

        info_0_val = ttk.Label(file_box, text="0 satellites and 0 trajectories in cache.")
        info_0_val.grid(row=info_row_0, column=1, columnspan=1, sticky="W")

        info_1_val = ttk.Label(file_box, text="0 unsaved satellites and 0 unsaved trajectories.")
        info_1_val.grid(row=info_row_1, column=1, columnspan=1, sticky="W")

        info_2_val = ttk.Label(file_box, text="Cache is up to date and matches selected location.")
        info_2_val.grid(row=info_row_2, column=1, columnspan=1, sticky="W")

        info_3_val = ttk.Label(file_box, text="TLE decay <now - tle_timestamp>.")
        info_3_val.grid(row=info_row_3, column=1, columnspan=1, sticky="W")

        info_4_val = ttk.Label(file_box, text="Calculations for <trajectory_end - now>")
        info_4_val.grid(row=info_row_4, column=1, columnspan=1, sticky="W")


        ############################################ Options Box ############################################
        #####################################################################################################
        option_box = ttk.Frame(self.parent)
        option_box.pack(padx=0, pady=2, fill='both', expand=True)
        ################################ RADIUS ################################
        radius_label = ttk.Label(option_box, text="Radius:")
        radius_label.grid(row=0, column=0, columnspan=1, sticky="E")
        radii = ['Radius', '1m', '10m', '100m', '1000m', '10000m']
        choice = tk.StringVar()
        radius_box = ttk.OptionMenu(option_box, choice, *radii).grid(row=0, column=1, columnspan=1, sticky='W')
        choice.set(radii[3])
        ################################ TIMESTEP ################################
        timestep_label = ttk.Label(option_box, text="Stepsize:")
        timestep_label.grid(row=0, column=2, columnspan=1, sticky="E")
        steps = ['Stepsize', '1sec', '1min', '10min', '1h', '2h']
        choice = tk.StringVar()
        time_box = ttk.OptionMenu(option_box, choice, *steps)
        time_box.grid(row=0, column=3, columnspan=1, sticky='W')
        choice.set(steps[1])
        ################################ RUNTIME ################################
        runtime_label = ttk.Label(option_box, text="Runtime:")
        runtime_label.grid(row=0, column=4, columnspan=1, sticky="E")
        steps = ['Runtime', '1h', '1D', '1W', '2W', '1M', '2M']
        choice = tk.StringVar()
        time_box = ttk.OptionMenu(option_box, choice, *steps)
        time_box.grid(row=0, column=5, columnspan=1, sticky='W')
        choice.set(steps[1])
        ################################ APPEND FLAG ################################
        append_trajectories = 1
        append_val = ttk.Checkbutton(option_box, text='Append',variable=append_trajectories, onvalue=1, offvalue=0, command=None)
        append_val.grid(row=0, column=6, sticky='W')
        ################################ RENDERBUTTON ################################
        calculate_button = ttk.Button(option_box, text="Calculate Trajectories", command=self.trajectories.calculate)
        calculate_button.grid(row=1, column=1, columnspan=2, sticky='W', padx=0)
        calc_start_label = ttk.Label(option_box, text="From: DD.MM.YYYY - hh:mm\tTo:DD.MM.YYYY - hh:mm")
        calc_start_label.grid(row=1, column=3, columnspan=5, sticky='W', padx=0)


        option_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)


        ############################################ Playback Box ############################################
        ######################################################################################################
        playback_box = ttk.Frame(self.parent)
        playback_box.pack(padx=0, pady=2, fill='both', expand=True)
        playback_label = ttk.Label(playback_box, text="Simulation:")
        playback_label.grid(row=0, column=0, columnspan=1, sticky="E")
        self.play_button = ttk.Button(playback_box, text="Run", command=self.toggle_sim_running)
        self.play_button.grid(row=0, columnspan=1, column=1, sticky='W', padx=0)

        self.clock_label = ttk.Label(playback_box, text="Monday, 01.01.2000, 00:00:00 <time.now>")
        self.clock_label.grid(row=0, column=2)
        self.clock_label.configure()
        self.clock(self.clock_label)

        playback_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)


        ############################################ Satellite Box ############################################
        ######################################################################################################
        satellite_box = ttk.Frame(self.parent)
        satellite_box.pack(padx=0, pady=2, fill='both', expand=True)
        inrange_label = ttk.Label(satellite_box, text="In Range:")
        inrange_label.grid(row=0, column=0, columnspan=1, sticky="NE")

        dummies = ("Sputnik 2", "ISS")
        var = tk.Variable(value=dummies)

        inrange_list = tk.Listbox(satellite_box, listvariable=var, selectmode = tk.SINGLE, width=66)
        inrange_list.grid(row=0, column=1)

        satellite_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)

        print("Info: UI intialized")

    def location_submit(self, event=None):
        self.loc_list = []
        self.loc_list_ui.delete(0, tk.END)
        input = location_query(self.location.get())
        if input:
            for i in range(len(input)):
                
                self.loc_list.append(input[i]) 
                
        for i in range(len(self.loc_list)):
            s =  self.loc_list[i][0] + str(self.loc_list[i][1])
            self.loc_list_ui.insert(tk.END, s) 
            
            self.loc_list_ui.itemconfig(i, 
                    bg = "#3498db" if i % 2 == 0 else "#e6b0aa") 
        
    def location_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            try:
                data = self.loc_list[index][1]
                lat, lon = data[0], data[1]
                s = "Lat.: %f°\t Lon.: %f°"%(lat, lon)
                
                txt = [i.strip() for i in self.loc_list[index][0].split(',')]
                
                country = txt.pop()
                zip = txt.pop()
                distr = txt.pop()
                city = txt[-1]
                addr = txt[1:-1]
                selected = txt[0]

                self.select_val.configure(text=selected)
                self.address_val.configure(text=addr)
                self.zip_val.configure(text=zip)
                self.city_val.configure(text=city)
                self.district_val.configure(text=distr)
                self.country_val.configure(text=country)
                self.lat_val.configure(text=lat)
                self.lon_val.configure(text=lon)

            except IndexError:
                pass
            
        else:
            self.select_val.configure(text="No location selected.")
            self.lat_val.configure(text="")
            self.lon_val.configure(text="")

        self.locations_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=1)
        
    def tle_open(self):
        self.tle_val = askopenfilename()
        if self.tle_val:
            self.tle_open_button.configure(text=self.tle_val)
        else:
            self.tle_open_button.configure(text="Open")

    def tle_new(self):
        print("Info: Querying new TLE data")
        print("Info: TLE data aquired")

    def tle_save(self):
        print("Info: TLEs saved to <file>")

    def trajectories_open(self):
        self.trajectories_val = askopenfilename()
        if self.trajectories_val:
            self.trajectories_open_button.configure(text=self.trajectories_val)
        else:
            self.trajectories_open_button.configure(text="Open")

    def trajectories_new(self):
        print("Info: Trajectories reset")

    def trajectories_save(self):
        print("Info: Trajectories saved to <file>")

    def config_open(self):
        self.config_val = askopenfilename()
        if self.config_val:
            self.config_open_button.configure(text=self.config_val)
        else:
            self.config_open_button.configure(text="Open")

    def config_new(self):
        print("Info: Config reset")

    def config_save(self):
        print("Info: Config save to <file>")

    def toggle_sim_running(self):
        self.sim_running = (self.sim_running != True)
        if self.sim_running:
            self.play_button.configure(text='Stop')
            self.play_button.configure(style="Highlight.TButton")
            self.clock_label.configure(style="Highlight.TLabel")
            self.engine.start()
            
        else:
            self.play_button.configure(text='Run')
            self.play_button.configure(style="Regular.TButton")
            self.clock_label.configure(style="Regular.TLabel")
            self.engine.stop()

    def clock(self, clock_label):
        t = time
        current_day = t.strftime("%d.%m.%Y")
        current_time = t.strftime("%H : %M : %S")
        clock_label.configure(text=current_day + ' - ' + current_time)
        clock_label.after(200, self.clock, clock_label)
        return time
