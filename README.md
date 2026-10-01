# multitrack

> DISCLAIMER : This branch is the [maximebrison](https://github.com/maximebrison)'s cut of the Multitrack project from [MSF-Telecom](https://github.com/MSF-Telecom) started by [fred-corp](https://github.com/fred-corp) and [ManoDaSilva](https://github.com/ManoDaSilva) in 2024.
> They mainly focused on the **implementation constraints**, the **features needed**, the **reverse-engineering the radios serial commands**, the **POC** and the main **skeleton**. 
> On my hand, I rewrote the JavaScript in **TypeScript**, implemented **front-end frameworks** (e.g. SolidJS), polished the **UI**, **future-proofed the code** and implemented some features. 

## Overview

Multitrack is an open-source software that passes commands/messages from radios (via and RS232 interface) to tracking/dispatching sytems.

## Features

This initial version is able to connect to an ICOM radio (IDAS/NXDN or dPMR), parse the GPS positions received and send them to Traccar. It handles various cases such as channel changes. Text messaging isn't implemented yet, nor are positions requests (at this time).

## User setup - ONLY FOR PROOF OF CONCEPT (Documentation coming soon)

No one-click setup is available just yet. However, the process is quite straightforward

### Getting Traccar running

- [Download and install](https://www.traccar.org/download/) Traccar locally
- Restart the computer (or start the traccar service manually)
- Open a web browser page and browse to: [http://localhost:8082/](http://localhost:8082/)
- You should be greeted by a traccar welcome page. Create a user and password, login.
- On the main interface click on the "Add" button (the plus sign). Set a name, and the identifier (Radio ID). Click save.
- [Refer to Traccar's documentation](https://www.traccar.org/documentation/) for more information on this interface's use.

### Getting Multitrack running

- Make sure you have connected an appropriate radio, with command output enabled (for Icom Radios: PC-CMDV2). Identify the COM port and speed.
- [Download](https://github.com/MSF-Telecom/multitrack/releases) the latest release of Multitrack.
- Extract the .zip in an empty folder.
- Edit config.ini to match your settings (Radio Port and Speed are the most important). Other settings should be left as default.
- Run main.exe. It should display the radio's serial number. As soon as a GPS position makes it to the radio, you should be notified by a line in the console, and the position should appear on Traccar's interface.

## Troubleshooting

Most common errors are either a wrong COM port, bad radio configuration or absent traccar entry for the radio you wish to track. Most of them can be narrowed down by looking in the logfiles.

### Traccar

Logfiles can be found in the default's program folder, under the \log directory.

### Multitrack

No logfiles are implemented yet. However, the console's output will help in narrowing down the reason.

## Dev notes

This initial version has been developed on a Windows 10 computer. However, no issues should come up when running it under Linux or MacOS.
Here are the tools used:

- Python 3.12 with pip
- git
- Python libraries: pyserial, pynmea2, configparser
- Traccar

After installing and setting up Traccar, the following lines will allow to create a dev environment:

```zsh
pip install pyserial pynmea2 configparser requests
git clone https://github.com/MSF-Telecom/multitrack/
cd multitrack
```

Optional, create a virtual environment :

```zsh
python3 -m venv ./venv
source ./venv/bin/activate
```

Continue install :

```zsh
git submodule init
git submodule update
cd python
python main.py
```

If you wish to update your copy to the latest commit (including its submodules):

```zsh
git checkout master
git submodule update --remote --merge
```

Verbosity levels can be changed in main.py's first lines.

## Roadmap

- Implement an easy-to-use GUI
- Implement message/SDS handling
- Implement automatic traccar updates with new messages
