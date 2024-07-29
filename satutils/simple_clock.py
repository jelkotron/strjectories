#!/home/schnollie/.venvs/strwueue/bin/python

#import all the required libraries first
import sys
from tkinter import *
#import time library to obtain current time
import time
 
text = "Computer sagt nein."

location = ""

def change_color(val, min, max):
    # TODO: make toggle conditional  
    # if val > min and val < max:
    if val % 2 == 0:
        color = "red"
        text = "Computer sagt nein."
    else:
        color = "green"
        text = "Jawohl!"

    text_elem.config(text=text)
    clock.configure(bg=color)


#create a function timing and variable current_time
def timing():
    t = time
    current_day = t.strftime("%Y.%m.%d")
    current_time = t.strftime("%H : %M : %S")
    calendar.config(text=current_day)
    clock.config(text=current_time)

    change_color(int(t.strftime("%S")), 30, 60)

    clock.after(200,timing)
 

def greet():
    print("Hollow World")

root=Tk()
root.geometry("800x600")


location_entry = Entry(root, textvariable=location)
location_entry.grid(row=0, column=1)
location_label = Label(location_entry, text="Location:")
location_button = Button(root, text="Login", command=greet)
location_button.grid(row=0, column=2)

text_elem = Label(root,font=("arial",20))
text_elem.grid(row=2,column=2,pady=25,padx=100)

calendar = Label(root,font=("arial",60))
calendar.grid(row=4,column=2,pady=25,padx=100)

clock = Label(root,font=("arial",60))
clock.grid(row=6,column=2,pady=25,padx=100)


timing()
root.mainloop()




































"""
#create a variable for digital clock
digital=Label(root,text="AskPython's Digital Clock",font="times 24 bold")
digital.grid(row=0,column=2)
 
nota=Label(root,text="hours        minutes        seconds",font="times 15 bold")
nota.grid(row=3,column=2)
""" 
 