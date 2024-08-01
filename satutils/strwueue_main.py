#!/home/schnollie/.venvs/strwueue/bin/python
import tkinter as tk
from strwueue_ui import Ui
from strwueue_engine import Engine
from strwueue_trajectories import Trajectories

title = 'STRWÜÜ'
geometry = "800x900"
resize_x = False
resize_y = True

def main(root):
    engine = Engine()
    trajectories = Trajectories()
    ui = Ui(root, engine, trajectories)
    root.mainloop()

if __name__ == "__main__":   
    root = tk.Tk()
    root.geometry(geometry)
    root.resizable(resize_x, resize_y)
    root.title(title)
    main(root)