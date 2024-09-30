# strjectories
A satellite tracking software to monitor the sky above a given location. While it should run on most systems supporting Python3, it is designed to run on a Raspberry Pi 5 and is used to drive a robotic artwork by media artist duo <i>strwüü</i>.

## Installation
It is recommended to use a virtual environment.

### Debian based OS
Install-, Update- and Lauch scripts for Debian based systems like Ubuntu or Raspbian are included in the repostory. After downloading the repository the scripts can be launched from command line or by double clicking the files. The scripts use venv by default. If you wish to use another or no virtual environment, see manual installation steps in <i>Other OS</i>   
### Other OS
On other systems, dependencies need to be installed manually. Open a terminal and navigage to the strjectories folder you have just downloaded. `pip install requirements` will install the python packages required to run strjectories. If your systems default python version is 2.x, make sure you have Python3 installed and use `pip3 install requirements`.

## Quickstart
Note: Headless mode (no UI) is not interactive. You should run the UI at least once to download data and set your configuration. After you have saved your config and data, you can change settings by modifying the json files created. TODO: Add 'blank' config/data files.   
### Debian based OS
After installation, you can exectue `lauch` from either a terminal or by clicking on it. If you have chosen to create a desktop icon during installation, you can use that as well.
To launch the application without UI, use `launch_noui`.
### Other OS
Open a terminal, navigate to the strjectories folder and and type `python3 scripts/main.py`.
To launch the application without UI, type `python3 scripts/main.py -b`.

### GUI
![STRJECTORIES](./assets/screenshot0.jpeg)
![STRJECTORIES](./assets/screenshot1.jpeg)
![STRJECTORIES](./assets/screenshot2.jpeg)