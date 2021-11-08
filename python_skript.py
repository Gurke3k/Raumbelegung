import time
import requests as req
import datetime
import icalendar
import pytz

ics_url = "https://stundenplanung.eah-jena.de/ical/raum/SPLUSF88401.ics" #ICS-Datei mit Belegungsdaten für Raum 03.03.33

def getics(): #Herunterladen und Speichern der ICS
    with req.get(ics_url) as rq:
        with open('room_03-03-33.ics', 'wb') as file:
            file.write(rq.content)
            file.close()

def readics(): #Lesen der ICS-Datei als iCalendar-Objekt und Rückgabe
    icalfile = open('room_03-03-33.ics')
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    return gcal

def lookevents(gcal): #Sucht im iCalendar nach Events, die mit der lokalen Zeit übereinstimmen 
    
    iEcount = 0 #Anzahl der Events
    bStatus = False #Raumstatus FALSE = frei, TRUE = belegt
    currentTimeDate = datetime.datetime.today() #local time not utc
    
    for component in gcal.walk(): #Durchsuche ics
        
        if component.name == "VEVENT": #Falls Event auftaucht
            
            #Speichert die Komponenten eines Events in Variablen
            summary = component.get('summary')
            startdt = component.get('dtstart').dt
            enddt = component.get('dtend').dt
            #exdate = component.get('exdate')
            #description = component.get('description')
            #location = component.get('location')

            #Prüfe ob es eine zeitliche Übereinstimmung in der Eventliste gibt
            if(currentTimeDate == startdt): #Übereinstimmung
                           
                bStatus = True
            
            else: #keine Übereinstimmung
                
                bStatus = False

            iEcount = iEcount + 1
            
            tdeltaDauer = enddt - startdt #Berechne Event Dauer 
            tdeltaRestdauer = enddt - currentTimeDate #Berechne Restdauer eines Events

            print(summary)
            print(startdt)
            print(enddt)
            print(tdeltaDauer)
            print(tdeltaRestdauer)

    return bStatus

def main():

    while True:
        
        gcal = readics()
        bStatus = lookevents(gcal) #Durchsucht ics-Datei nach aktuellen Events und speichert den Status
        
        if(bStatus == False):
            #Sende Information über Raumbelegung an Display
            #Je nach Veranstaltungdauer, pausiere Zeit
            print("Raum frei")
            time.sleep(60) #Pausiere Ablauf des Skripts für 60 s
        else:
            #Sende Information über Raumbelegung an Display
            print("Raum belegt")
            time.sleep(60)




getics() #einmal pro Tag soll das BS die ics-Datei der EAH Stundenplanwebseite abrufen
main() #anschließend soll dieses Skript laufen









