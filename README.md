# Raumbelegung
Twp Raumbelegung

Project for "Ernst-Abbe-Hochschule" Jena

Members:


Folders:

-DrawImgNew:
  - for testing Layout files without Rasp. Pi and E-Paper display

- E-Paper Anzeige
  -  Final project for Rooms of "EAH"

  Usage on Pi:
    - setup raspberry Pi (
        sudo apt-get update
        sudo apt-get install python-pip
        sudo apt-get install python-pil
        sudo apt-get install python-numpy
        sudo pip install RPi.GPIO
        
    - Clone Folder E-Paper Anzeige
    - install missing reopsitories via pip install
        pip install datetime
        pip install PIL
        pip install icalendar
        pip install requests
    
    - run the Script Terminverarbeitung.py in folder examples

    - for config to different rooms: change:
      ics_url (line 26)
      staticTextRoom (line 28)
      (only needed if multiple copys of script used in same folder:) change ics references (line 51, line 57)     
      
