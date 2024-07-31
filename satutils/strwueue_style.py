from tkinter.ttk import Style

def style(variant=None):
    style = Style()
    if not variant:
        style.configure("Regular.TButton", foreground="black")
        style.configure("Regular.TLabel", foreground="black")
        style.configure("Highlight.TButton", foreground="red")
        style.configure("Highlight.TLabel", foreground="red")
    return style
