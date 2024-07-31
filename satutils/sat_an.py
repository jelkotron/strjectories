#!/home/schnollie/.venvs/strwueue/bin/python
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter.messagebox import showinfo
from geopy import geocoders



# root window
root = tk.Tk()
root.geometry("800x900")
root.resizable(True, True)
root.title('STRWÜÜ')

# store email address and password
location = tk.StringVar()

lat = "0"
lon = "0"
gn = geocoders.Nominatim(user_agent="my_App")

config_val = None
tle_val = None
trajectories_val = None
loc_list = []

def login_clicked():
    global loc_list
    loc_list = []
    list.delete(0, tk.END)
    input = gn.geocode(location.get(), exactly_one=False)
    if input:
        for i in range(len(input)):
            
            loc_list.append(input[i]) 
            
    for i in range(len(loc_list)):
        s =  loc_list[i][0] + str(loc_list[i][1])
        list.insert(tk.END, s) 
        
        list.itemconfig(i, 
                bg = "#3498db" if i % 2 == 0 else "#e6b0aa") 
      
def city_selected(event):
    global loc_list
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        try:
            data = loc_list[index][1]
            lat, lon = data[0], data[1]
            s = "Lat.: %f°\t Lon.: %f°"%(lat, lon)
            
            txt = [i.strip() for i in loc_list[index][0].split(',')]
            
            country = txt.pop()
            zip = txt.pop()
            distr = txt.pop()
            city = txt[-1]
            addr = txt[1:-1]
            selected = txt[0]


            select_val.configure(text=selected)
            address_val.configure(text=addr)
            zip_val.configure(text=zip)
            city_val.configure(text=city)
            district_val.configure(text=distr)
            country_val.configure(text=country)



            lat_val.configure(text=lat)
            lon_val.configure(text=lon)

        except IndexError:
            pass
        
    else:
        select_val.configure(text="No location selected.")
        lat_val.configure(text="")
        lon_val.configure(text="")

    locations_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=1)
    
def open_tle_clicked():
    global tle_val
    tle_val = askopenfilename()
    if tle_val:
        open_tle_button.configure(text=tle_val)
    else:
        open_tle_button.configure(text="Open")

def open_trajectories_clicked():
    global trajectories_val
    trajectories_val = askopenfilename()
    if trajectories_val:
        open_trajectories_button.configure(text=trajectories_val)
    else:
        open_tle_button.configure(text="Open")

def open_config_clicked():
    global config_val
    config_val = askopenfilename()
    if config_val:
        open_config_button.configure(text=config_val)
    else:
        open_config_button.configure(text="Open")



############################################ Location Box ############################################
######################################################################################################
locations_box = ttk.Frame(root)
locations_box.pack(padx=0, pady=2, fill='both', expand=True)

email_label = ttk.Label(locations_box, text="Location:")
email_entry = ttk.Entry(locations_box, textvariable=location)
login_button = ttk.Button(locations_box, text="OK", command=login_clicked)
list = tk.Listbox(locations_box, selectmode = tk.SINGLE, width=66)

email_label.grid(row=0, column=0, columnspan=1)
email_entry.grid(row=0, column=1, columnspan=5, padx=2, pady=2, sticky="EW")
login_button.grid(row=0, column=6, padx=2, pady=2)
list.grid(row=1, column=1, columnspan=6, rowspan=8, padx=2, pady=2, sticky='EW')
locations_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=0)

############################################ Selection Box ############################################
#######################################################################################################
selection_box = ttk.Frame(root)
selection_box.pack(padx=0, pady=2, fill='both', expand=True)

select_label = ttk.Label(selection_box, text="Selection:")
select_val = ttk.Label(selection_box, text="")

address_label = ttk.Label(selection_box, text="Address:")
address_val = ttk.Label(selection_box, text="")

zip_label = ttk.Label(selection_box, text="Zip Code:")
zip_val = ttk.Label(selection_box, text="")

city_label = ttk.Label(selection_box, text="City:")
city_val = ttk.Label(selection_box, text="")


district_label = ttk.Label(selection_box, text="District:")
district_val = ttk.Label(selection_box, text="")

country_label = ttk.Label(selection_box, text="Country:")
country_val = ttk.Label(selection_box, text="")

lat_label = ttk.Label(selection_box, text="Latitude:")
lat_val = ttk.Label(selection_box, text="")

lon_label = ttk.Label(selection_box, text="Longitude:")
lon_val = ttk.Label(selection_box, text="")

select_label.grid(row=0, column=0, columnspan=1, sticky="E")
select_val.grid(row=0, column=1, sticky="W")

address_label.grid(row=1, column=0, columnspan=1, sticky="E")
address_val.grid(row=1, column=1, sticky="W")

zip_label.grid(row=2, column=0, columnspan=1, sticky="E")
zip_val.grid(row=2, column=1, sticky="W")

city_label.grid(row=3, column=0, columnspan=1, sticky="E")
city_val.grid(row=3, column=1, sticky="W")

district_label.grid(row=4, column=0, columnspan=1, sticky="E")
district_val.grid(row=4, column=1, sticky="W")

country_label.grid(row=5, column=0, columnspan=1, sticky="E")
country_val.grid(row=5, column=1, sticky="W")

lat_label.grid(row=6, column=0, columnspan=1, sticky="E")
lat_val.grid(row=6, column=1, sticky="W")

lon_label.grid(row=7, column=0, columnspan=1, sticky="E")
lon_val.grid(row=7, column=1, sticky="W")

selection_box.columnconfigure((0,1,2,3,4,5,6,7,8,9,10),minsize=100, weight=0)




############################################ File Box ############################################
##################################################################################################
file_box = ttk.Frame(root)
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
open_config_button = ttk.Button(file_box, text="Open", command=open_config_clicked)
open_config_button.grid(row=config_row, column=1, sticky='EW', padx=0)

get_config_button = ttk.Button(file_box, text="New")
get_config_button.grid(row=config_row, column=2, sticky='WE', padx=0)

save_config_button = ttk.Button(file_box, text="Save")
save_config_button.grid(row=config_row, column=3, sticky='W', padx=0)

################################ TLE ################################
tle_label = ttk.Label(file_box, text="TLEs:").grid(row=tle_row, column=0, columnspan=1, sticky="E")
open_tle_button = ttk.Button(file_box, text="Open", command=open_tle_clicked)
open_tle_button.grid(row=tle_row, column=1, sticky='EW', padx=0)

get_tle_button = ttk.Button(file_box, text="New")
get_tle_button.grid(row=tle_row, column=2, sticky='WE', padx=0)

save_tle_button = ttk.Button(file_box, text="Save")
save_tle_button.grid(row=tle_row, column=3, sticky='W', padx=0)

################################ TRAJECTORIES ################################
trajectories_label = ttk.Label(file_box, text="Trajectories:")
trajectories_label.grid(row=trajectory_row, column=0, columnspan=1, sticky="E")

open_trajectories_button = ttk.Button(file_box, text="Open", command=open_trajectories_clicked)
open_trajectories_button.grid(row=trajectory_row, column=1, sticky='EW', padx=0)

get_trajectories_button = ttk.Button(file_box, text="New")
get_trajectories_button.grid(row=trajectory_row, column=2, sticky='WE', padx=0)

save_trajectories_button = ttk.Button(file_box, text="Save")
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
option_box = ttk.Frame(root)
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
calculate_button = ttk.Button(option_box, text="Calculate Trajectories")
calculate_button.grid(row=1, columnspan=5, column=1, sticky='W', padx=0)

option_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)
option_box.rowconfigure(1, pad=10)

############################################ Playback Box ############################################
######################################################################################################
playback_box = ttk.Frame(root)
playback_box.pack(padx=0, pady=2, fill='both', expand=True)
playback_label = ttk.Label(playback_box, text="Simulation:")
playback_label.grid(row=0, column=0, columnspan=1, sticky="E")
play_button = ttk.Button(playback_box, text="Run")
play_button.grid(row=0, columnspan=1, column=1, sticky='W', padx=0)

clock_label = ttk.Label(playback_box, text="Monday, 01.01.2000, 00:00:00 <time.now>")
clock_label.grid(row=0, column=2)


playback_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)
############################################ Satellite Box ############################################
######################################################################################################
satellite_box = ttk.Frame(root)
satellite_box.pack(padx=0, pady=2, fill='both', expand=True)
inrange_label = ttk.Label(satellite_box, text="In Range:")
inrange_label.grid(row=0, column=0, columnspan=1, sticky="NE")

dummies = ("Sputnik 2", "ISS")
var = tk.Variable(value=dummies)

inrange_list = tk.Listbox(satellite_box, listvariable=var, selectmode = tk.SINGLE, width=66)
inrange_list.grid(row=0, column=1)

satellite_box.columnconfigure((0,1,2,3,4,5,6,7,8),minsize=100, weight=0)





list.bind('<<ListboxSelect>>', city_selected)


"""

login_button.grid(row=0, column=5, columnspan=1)
email_entry.pack(fill='x', expand=True)

# login button
login_button.pack(fill='x', expand=True, pady=10)


email_entry.focus()

list.pack(expand=False, fill=tk.BOTH) 
  
  
loc_label = tk.Label(locations_box, text="Please enter a location.")
loc_label.pack()

"""


# var1 = False
# var2 = False
# var3 = False

# c00 = tk.Label(root, bg='white', width=20, text='empty')
# c01 = tk.Checkbutton(locations_box, text='10m',variable=var1, onvalue=1, offvalue=0, command=None)
# c02 = tk.Checkbutton(locations_box, text='100m',variable=var2, onvalue=1, offvalue=0, command=None)
# c03 = tk.Checkbutton(locations_box, text='1000m',variable=var3, onvalue=1, offvalue=0, command=None)
# c04 = tk.Checkbutton(locations_box, text='10000m',variable=var3, onvalue=1, offvalue=0, command=None)

# c01.pack()
# c02.pack()
# c03.pack()
# c04.pack()


root.mainloop()