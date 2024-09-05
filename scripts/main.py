#!/usr/bin/env python3
from ui import Gui
from config import ConfigIo

def main():
    config = ConfigIo()
    ui = Gui(config,
        title_main="STRJECTORIES",
        resizable_main=(False, False),
        geometry_main="800x800+800+0",
       
        title_viewer="STRVIEW",
        resizable_viewer=(False, False),
        geometry_viewer='800x600+0+0',
        background_viewer='DEFAULT'
    )
        
    if ui.root:
        ui.root.mainloop()


if __name__ == "__main__":   
    main()
