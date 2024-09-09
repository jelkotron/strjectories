from tkinter.ttk import Style

def style(variant=None):
    style = Style()

    buttoncolor = 'grey20'
    buttoncolor_disabled = 'grey22'
    bg = 'grey25'
    txt_0 = 'white'
    txt_1 = 'grey90'
    txt_2 = 'grey80'
    txt_3 = 'grey70'
    txt_4 = 'grey60'
    txt_5 = 'grey50'

    if not variant:
        style.theme_use("clam")
        style.configure("Root",
            background='black',
            )
        
        style.configure("Dark.TFrame", 
            background=bg, 
            highlightcolor='grey50',
            highlightthickness=2,
            darkcolor='grey10',
            )
        
        style.configure("Dark.TNotebook", 
            background=bg, 
            bordercolor = 'black',
            lightcolor=bg,
            darkcolor=bg,
            border=1,
            )

        style.configure("Dark.TNotebook.Tab",
            background=bg, 
            # foreground = 'white',
            border=1,
            lightcolor=bg,
            darkcolor=bg,
            bordercolor = 'black',
            foreground = 'white'
            )

        style.map('Dark.TNotebook.Tab', 
            foreground = [('disabled', txt_1), ('active', txt_1), ('selected', txt_1), ('!active', txt_5)],
            background = [('active', bg), ('!active', bg)],
            lightcolor = [('active', bg), ('!active', bg)],
            darkcolor = [('active', bg), ('!active', bg)],
            bordercolor = [('!active', '!selected', bg), ('active', 'selected', 'black'), ('disabled', 'active', '!active', bg)]
            )
                    

        style.configure("Regular.TLabel", background="#2C2828", foreground="white")

        
        
        style.configure("Highlight.TButton", 
            background="#2C2C2C", 
            foreground="red", 
            bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
            lightcolor=bg,
            darkcolor='grey10',
            padding=(0,2),
            )
        
        style.map("Highlight.TButton",
            foreground = [('active', '!disabled', 'red'), ('!active', 'red')],
            background = [('active', 'black'), ('!active', buttoncolor)],

            )


        style.configure("Highlight.TLabel", background=bg, foreground=txt_0)
        style.map("Highlight.TLabel",
                    background=[("!disabled", bg), ("disabled", bg)],
                    foreground=[("!disabled", txt_0), ("disabled", txt_5)],

        )
        style.configure("Dark.TLabel", background=bg, foreground=txt_3)
        style.map("Dark.TLabel",
                    background=[("!disabled", bg), ("disabled", bg)],
                    foreground=[("!disabled", txt_3), ("disabled", txt_5)],

        )


        style.configure("BoldDark.TLabel", background=bg, foreground=txt_1)


        style.configure('Dark.TButton', 
                        bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                        lightcolor=bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=12,
                        )
        
        style.map('Dark.TButton', 
                    foreground = [('active', '!disabled', 'white'), ('!active', txt_3)],
                    background = [('active', buttoncolor), ('!active', buttoncolor)],
                    
                    )



        style.configure("Dark.TMenubutton", 
                        bordercolor = 'black',
                        lightcolor=bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=10,
                        )
        
        style.configure("DarkFixed.TMenubutton",
                        bordercolor = 'black',
                        lightcolor=bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=18,
                        )
        
        style.map("DarkFixed.TMenubutton", 
                    foreground = [('disabled', txt_5), ('active', '!disabled', txt_0), ('!active', txt_2)],
                    background = [('disabled', buttoncolor_disabled), ('active', buttoncolor), ('!active', buttoncolor)],
                    # disabledbackground = [(('active', 'red'), ('!active', 'blue')],
                    )
        
        style.map("Dark.TMenubutton", 
                    foreground = [('disabled', txt_5), ('active', '!disabled', txt_0), ('!active', txt_2)],
                    background = [('disabled', buttoncolor_disabled), ('active', buttoncolor), ('!active', buttoncolor)],
                    # disabledbackground = [(('active', 'red'), ('!active', 'blue')],
                    )
        
        

        style.configure("Dark.TEntry",
                    fieldbackground="grey17",
                    background="grey17",
                    height=50,
                    foreground=txt_0,
                    bordercolor = bg,#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                    lightcolor='grey40',
                    padding=(0,4),
                    darkcolor='black'   
                        )
        
        
        style.configure('Dark.TCheckbutton', 
                bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                lightcolor=bg,
                darkcolor='grey10',
                highlightcolor='red',
                background=bg)
        
        style.map('Dark.TCheckbutton', 
                foreground = [('active', '!disabled', 'white'), ('!active', txt_3)],
                background = [('active', bg), ('!active', bg),],
                indicatorbackground = [('!selected', 'red'), ('selected', 'green')],
                indicatorforeground = [('!selected', 'black'), ('selected', 'black')],

                    )

        
    return style
