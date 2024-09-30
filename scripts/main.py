#!/usr/bin/env python3
import sys
from ui import Gui
from config import ConfigIo

def main(background=False):
    config = ConfigIo()
    if not background:
        ui = Gui(config,
            title_main="STRJECTORIES",
            resizable_main=(False, True),
            geometry_main="800x900+800+0",
        
            title_viewer="STRVIEW",
            resizable_viewer=(False, False),
            geometry_viewer='800x600+0+0',
            background_viewer='DEFAULT'
        )
            
        if ui.root:
            ui.root.mainloop()


if __name__ == "__main__":
    background = False  
    for i in sys.argv:
        if i == '-b':
            background = True  

    main(background)
