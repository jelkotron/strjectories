#!/home/schnollie/.venvs/strwueue/bin/python
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from geopy import geocoders




# root window
root = tk.Tk()
root.geometry("800x600")
root.resizable(False, False)
root.title('Set Location')

# store email address and password
location = tk.StringVar()

lat = "0"
lon = "0"

gn = geocoders.Nominatim(user_agent="my_App")

loc_list = []

def login_clicked():
    global loc_list
    loc_list = []
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
            loc_label.configure(text=s)
        except IndexError:
            pass
        
    else:
        loc_label.configure(text="No location selected.")

# Sign in frame
signin = ttk.Frame(root)
signin.pack(padx=10, pady=10, fill='x', expand=True)


# email
email_label = ttk.Label(signin, text="Location:")
email_label.pack(fill='x', expand=True)

email_entry = ttk.Entry(signin, textvariable=location)
email_entry.pack(fill='x', expand=True)

# login button
login_button = ttk.Button(signin, text="Get Location Data", command=login_clicked)
login_button.pack(fill='x', expand=True, pady=10)


email_entry.focus()

list = tk.Listbox(signin, selectmode = tk.EXTENDED)
list.pack(expand=False, fill=tk.BOTH) 
list.bind('<<ListboxSelect>>', city_selected)
  
  
loc_label = tk.Label(signin, text="Please enter a location.")
loc_label.pack()

var1 = False
var2 = False
var3 = False

# c00 = tk.Label(root, bg='white', width=20, text='empty')
c01 = tk.Checkbutton(signin, text='10m',variable=var1, onvalue=1, offvalue=0, command=None)
c02 = tk.Checkbutton(signin, text='100m',variable=var2, onvalue=1, offvalue=0, command=None)
c03 = tk.Checkbutton(signin, text='1000m',variable=var3, onvalue=1, offvalue=0, command=None)
c04 = tk.Checkbutton(signin, text='10000m',variable=var3, onvalue=1, offvalue=0, command=None)

c01.pack()
c02.pack()
c03.pack()
c04.pack()


root.mainloop()