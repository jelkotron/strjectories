#!/home/schnollie/.venvs/strwueue/bin/python
import tkinter as tk
from strwueue_ui import Ui

def main():
    root = tk.Tk()
    root.geometry("800x900")
    root.resizable(False, True)
    root.title('STRWÜÜ')
    ui = Ui(root)
    root.mainloop()

main()