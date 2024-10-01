# STRJECTORIES
A satellite tracking software to monitor the sky above a given location. While it should run on most systems supporting Python3, it is designed to run on a Raspberry Pi 5 to drive a robotic artwork by artist duo <i>strwüü</i>.
<br />
## Installation
It is recommended to use a virtual environment.

### Debian based OS
`install`, `update` and `lauch` scripts for Debian based systems like Ubuntu or Raspbian OS are included in the repository. After downloading the repository, the scripts can be launched from command line or by double clicking the files. The scripts create and use a virtual environment named <i>venv</i> inside the directory. If you wish to use another or no virtual environment, see manual installation steps in <i>Installation > Other OS</i>.  
### Other OS
On other systems, dependencies need to be installed manually. Open a terminal and navigage to the Strjectories folder you have just downloaded. Optionally create a virtual environment using `python3 -m venv venv`. Required step: `pip install -r requirements.txt` will install the python packages required to run Strjectories. If your systems default python version is 2.x, make sure you have Python3 installed and use `pip3 install -r requirements.txt` instead. 

<br />

## Quickstart
### Debian based OS
After installation, you can execute `lauch` from either a terminal or by clicking on it. If you have chosen to create a desktop icon during installation, you can click that as well.
To launch the application without UI, execute `launch_noui` from a terminal.
### Other OS
Open a terminal, navigate to the Strjectories folder. If you are using venv, activate the environment using `source <path to venv>/bin/activate`. To start Strjectories type `python3 scripts/main.py`. 
If you want to launch the application without UI, use `python3 scripts/main.py -b` instead.

   
### Run Simulation
The <i>STRJECTORIES</i> window of the UI lets you set up options for your simulation, detailed below. To run a simulation, you need enter a location and download data using the <i>Data/New</i> Button. Press <i>Start</i> to run the simulation.

<br />

## Viewer Window
![Screenshot of Viewer Window](assets/screenshot0.jpeg)
A map of satellites is rendered to this window. The viewer has a simple color coding: Red satellites are in range, all other satellites are fading between black and white depending on their distance from the target location. Satellites selected in the property window are outlined yellow. 

<br />

## Property Window
![Screenshot of Property Window](assets/screenshot1.jpeg)

### Location Panel
Enter an address or location in the search bar and select a result from the list. Much like using your favourite map service!

### Selection Panel
Displays additional information for the selected location and indicates if the system is sleeping.

### File Panel
Strjectories relies on two types of files, one that stores the configuration set in the UI and one to store satellite data. In the file panel you can create, open and save both file types. The files use JSON as a format. An additional line of text displays the number of active satellites, save states and the decay of the satellite data's precision.  

### Automation Panel
In this Panel you can choose, what the system does automatically and in which intervals. Options are:

+ <b>Auto Start Simulation:</b> If enabled, simulation starts upon load.


+ <b>Auto Save:</b> 
If enabled, changing a property triggers your config file being saved. Also, when simulating, newly calculated satellite data is written to disk in the interval set below.

+ <b>Auto Download:</b> 
If enabled, satellite data is updated in the interval set below. As satellite data becomes unprecise after a day or two, enable this option to keep your objects up to date.

+ <b>Auto Sleep:</b> 
If enabled, simulation is stopped between the two daytimes set below. Uses local time of selected location, 24h input.

+ <b>Auto Render:</b> 
If enabled, the viewer window gets updated with every change. Select the render range below choosing from <i>All, In Range, Primary,</i> and <i>Secondary</i>.  <b>Note: For users of systems with little resources, like the Raspberry Pi, rendering <i>all</i> is not recommended while running the simulation.</b>

+ <b>Render Step: </b> 
This option specifies, how often satellites are being rendered: while the calculation is running, the visual representation of each satellite is only updated every nth time. <b>Note: This option is usefull for users of systems with little system resources like the Raspberry Pi. Setting a render step greater than 0 can avoid GPU bottlenecks, UI freezes and crashes.</b> 

### Simulation Panel
Press <i>Start</i> to run the simulation.
Options are:
+ <b>Sort by:</b> Defines the order in that satellite are upated. Satellites can be sorted either by proximity to the selected location or by their velocity 
+ <b>Objects:</b> Calculations are split into 2 threads to allow faster updates for prioritized (closer or faster) objects  
+ <b>Range:</b> Defines the radius to identify satellites
+ <b>Class:</b> Filter satellites by classification (or don't, see <i>Trouble Shooting</i>) 
+ <b>Filter:</b> Filter objects by name  

### In Range Panel
Displays a list of satellites in range and their count.


### Output Panel
#### Pin Tab
<b>Note: Pin communication is only implemented for Raspberry Pi 5.</b> Strjectories can set 2 different GPIO pins depending on various options. Options for both 'slots' are the identical:
+ <b>Use: </b>Set the checkbox if you want to use this pin
+ <b>If: </b>Set the condition for setting the pin. Options are <i>(not) Sleeping</i> and <i>(no) Satellites in Range</i>. 
+ <b>Pin: </b>Raspberry Pi GPIO pin number
+ <b>Value: </b>Value to set pin to if condition is fulfilled  
+ <b>State: </b>This display shows the current state of the pin or previews it if the pin is not used

#### Serial Tab
+ <b>Use: </b>Set the checkbox if you want to use this serial port
+ <b>Port: </b>Set the serial port 
+ <b>Baud: </b>Set the serial baud rate
+ <b>Value: </b>Value to send. Options are <i>In Range Count</i> and <i>(no) Satellites in Range</i>

#### Log Tab
If <i>Log</i> is enabled and a log file is set using <i>open</i> or <i>new</i> , Strjectories logs things.
The maximum number of lines to log is set in the <i>Lines max</i> input field.

Events you can log are: 
+ Engine events
+ File I/O
+ Updates (Downloads)
+ Sleep/Wake
+ (In Range) List
+ (In Range) List Length
+ Pin I/O
+ Serial I/O





## Output Window
![Screenshot of Output Window](assets/screenshot2.jpeg)
The Ouput Window displays valuable Information: Engine events, File I/O, Downloads, Sleep/Wake. Depending on the way you have started Strjectories, this info might appear in the terminal you started the program from. <b>Warning: </b>Closing the Output window will terminate the application.

## Trouble Shooting

As Strjectories is still in early development, there are still bugs to be found and it is possible for the user to render the tool unusable, especially on systems with little resources. This section outlines recommendations to avoid problems and methods to fix some known issues.

### Launch after Crash
Sometimes Strjectories crashes and wont't start again, especially, when autosave is enabled. On a smaller systems this happens when using settings that are too demanding (see <i>Rendering on a Raspberry</i>). All systems can face similar issues when using questionable simulation settings (see <i>Simulation Properties</i>).

<b>Solution: </b>If Strjectories won't start, you can modify the config file you have last used with a text editor. If you don't know, which value causes your issue, you can delete or rename the config file so the tool starts without a config file set. If Strjectories crashed while writing data rendering the file broken, deleting and manually downloading new data will help. Alternatively you can modify or delete the sessiondata file in the Strjectories folder. 

### Simulation Properties 
+ <b>Sort by: </b> Sorting by velocity is of rare use for the in-range-detection scenario but can be useful for satellite observation in general. 
+ <b>Primary and secondary objects: </b>Depending on the use case, the number of primary objects should be greater than the number of satellites in range, to ensure prioritized detection of satellites entering or leaving the search area. The secondary object number doubles as a maximum number of satellites being calculated and rendered.</b> 

+ <b>Range: </b>The range value represents the radius of a circle around the target location. Earths circumfence is roughly 40.000km. Using a search radius greater than half the planets circumfence makes little sense and leads to unknown behaviour, possibly crashes and broken program start up. While Radii greater around 6000-8000 km beautifully illustrate the mercator projection, they are known to cause performance issues on most systems. Greater values are untested and not recommended to use. 

+ <b>Classification: </b>There are only unclassified objects in the data obtained from the current source.
### Rendering on a Raspberry
+ Unless you are rendering less than 10-20 satellites, a render step > 0 is strongly recommended.
+ Rendering <i>all</i> satellites is only recommended while the simulation is not running. It will still take time. Startup may slow down when rendering all is written to the config file, in combination with autosimulate startup may fail.
+ You can easily render 500+ satellites using a step of 16. You will still see the viewer update regularily as the render load is balanced when using a step.
+ There are two instances of time measurement in the UI: The local time clock in the selection panel and the running time displayed beaneath the start/stop button. While small stutters in ticking are normal, you should use a higher step if the interface freezes too much.
+ Using a monitoring tool such as the <i>Task Manager</i> in Raspbian OS can help you evaluate CPU and GPU load and set your options accordingly. 



### Running Headless
As of now, headless mode (no UI) is not interactive. You should run the UI at least once to download data and set your configuration. After you have saved your config and data files, you can use headless mode and change settings by modifying the files using a text editor.

### Running on Windows

Using Strjectories on Windows is untested. Usage of Python3, Pip and Venv may vary from instructions given. Users may have to replace `/` with `\` when following the instructions. It may necessary to use file extensions for file created with Strjectories like `config.json` or `data.json`. 