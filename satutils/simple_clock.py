#!/home/schnollie/.venvs/strwueue/bin/python

#import all the required libraries first
import sys
from tkinter import *
#import time library to obtain current time
import time
 
typeface = "bold"

def change_color(val, min, max):
    # TODO: make toggle conditional  
    if val > min and val < max:
        color = "red"
    else:
        color = "green"

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
 

root=Tk()
root.geometry("600x300")

calendar = Label(root,font=("arial",60))
calendar.grid(row=0,column=2,pady=25,padx=100)

clock = Label(root,font=("arial",60))
clock.grid(row=2,column=2,pady=25,padx=100)
timing()
root.mainloop()




































"""
#create a variable for digital clock
digital=Label(root,text="AskPython's Digital Clock",font="times 24 bold")
digital.grid(row=0,column=2)
 
nota=Label(root,text="hours        minutes        seconds",font="times 15 bold")
nota.grid(row=3,column=2)
""" 
 