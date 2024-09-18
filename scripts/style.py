from tkinter.ttk import Style

class StrStyle(Style):
    def __init__(self):
        super().__init__()
        self.buttoncolor = 'grey20'
        self.buttoncolor_disabled = 'grey22'
        self.bg = 'grey25'
        self.bg_alt1 = 'grey20'
        self.bg_alt2 = 'grey15'
        self.txt_0 = 'white'
        self.txt_1 = 'grey90'
        self.txt_2 = 'grey80'
        self.txt_3 = 'grey70'
        self.txt_4 = 'grey60'
        self.txt_5 = 'grey50'

        self.theme_use("clam")
        self.configure("Root",
            background='black',
            )
        
        self.configure("Dark.TFrame", 
            background=self.bg, 
            highlightcolor='grey50',
            highlightthickness=2,
            darkcolor='grey10',
            )
        
        self.configure("Dark.TNotebook", 
            background=self.bg, 
            bordercolor = 'black',
            lightcolor=self.bg,
            darkcolor=self.bg,
            border=1,
            )

        self.configure("Dark.TNotebook.Tab",
            background=self.bg, 
            # foreground = 'white',
            border=1,
            lightcolor=self.bg,
            darkcolor=self.bg,
            bordercolor = 'black',
            foreground = 'white'
            )

        self.map('Dark.TNotebook.Tab', 
            foreground = [('disabled', self.txt_1), ('active', self.txt_1), ('selected', self.txt_1), ('!active', self.txt_5)],
            background = [('active', self.bg), ('!active', self.bg)],
            lightcolor = [('active', self.bg), ('!active', self.bg)],
            darkcolor = [('active', self.bg), ('!active', self.bg)],
            bordercolor = [('!active', '!selected', self.bg), ('active', 'selected', 'black'), ('disabled', 'active', '!active', self.bg)]
            )
                    

        self.configure("Regular.TLabel", background="#2C2828", foreground="white")

        
        
        self.configure("Highlight.TButton", 
            background="#2C2C2C", 
            foreground="red", 
            bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
            lightcolor=self.bg,
            darkcolor='grey10',
            padding=(0,2),
            )
        
        self.map("Highlight.TButton",
            foreground = [('active', '!disabled', 'red'), ('!active', 'red')],
            background = [('active', 'black'), ('!active', self.buttoncolor)],

            )


        self.configure("Highlight.TLabel", background=self.bg, foreground=self.txt_0)
        self.map("Highlight.TLabel",
                    background=[("!disabled", self.bg), ("disabled", self.bg)],
                    foreground=[("!disabled", self.txt_0), ("disabled", self.txt_5)],

        )
        self.configure("Dark.TLabel", background=self.bg, foreground=self.txt_3)
        self.map("Dark.TLabel",
                    background=[("!disabled", self.bg), ("disabled", self.bg)],
                    foreground=[("!disabled", self.txt_3), ("disabled", self.txt_5)],

        )


        self.configure("BoldDark.TLabel", background=self.bg, foreground=self.txt_1)


        self.configure('Dark.TButton', 
                        bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                        lightcolor=self.bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=12,
                        )
        
        self.map('Dark.TButton', 
                    foreground = [('active', '!disabled', 'white'), ('!active', self.txt_3)],
                    background = [('active', self.buttoncolor), ('!active', self.buttoncolor)],
                    
                    )



        self.configure("Dark.TMenubutton", 
                        bordercolor = 'black',
                        lightcolor=self.bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=10,
                        )
        
        self.configure("DarkFixed.TMenubutton",
                        bordercolor = 'black',
                        lightcolor=self.bg,
                        padding=(0,2),
                        darkcolor='grey10',
                        anchor="center",
                        width=18,
                        )
        
        self.map("DarkFixed.TMenubutton", 
                    foreground = [('disabled', self.txt_5), ('active', '!disabled', self.txt_0), ('!active', self.txt_2)],
                    background = [('disabled', self.buttoncolor_disabled), ('active', self.buttoncolor), ('!active', self.buttoncolor)],
                    # disabledbackground = [(('active', 'red'), ('!active', 'blue')],
                    )
        
        self.map("Dark.TMenubutton", 
                    foreground = [('disabled', self.txt_5), ('active', '!disabled', self.txt_0), ('!active', self.txt_2)],
                    background = [('disabled', self.buttoncolor_disabled), ('active', self.buttoncolor), ('!active', self.buttoncolor)],
                    # disabledbackground = [(('active', 'red'), ('!active', 'blue')],
                    )
        
        

        self.configure("Dark.TEntry",
                    fieldbackground="grey17",
                    background="grey17",
                    height=50,
                    foreground=self.txt_0,
                    bordercolor = self.bg,#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                    lightcolor='grey40',
                    padding=(0,4),
                    darkcolor='black'   
                        )
        
        
        self.configure('Dark.TCheckbutton', 
                bordercolor = 'black',#)#[('active', 'disabled', 'black'), ('!active', 'black')])
                lightcolor=self.bg,
                darkcolor='grey10',
                highlightcolor='red',
                background=self.bg)
        
        self.map('Dark.TCheckbutton', 
                foreground = [('active', '!disabled', 'white'), ('!active', self.txt_3)],
                background = [('active', self.bg), ('!active', self.bg),],
                indicatorbackground = [('!selected', 'red'), ('selected', 'green')],
                indicatorforeground = [('!selected', 'black'), ('selected', 'black')],

                    )

        
  
