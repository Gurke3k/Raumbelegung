import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import time
from typing import ItemsView
from icalendar.prop import HOUR
import requests as req
import datetime
import icalendar
from PIL import Image, ImageDraw, ImageFont
import logging
from waveshare_epd import epd5in83b_V2
import traceback

logging.basicConfig(level=logging.DEBUG) #??

#Programmbeschreibung
#Exception falls es zu einem Fehler beim Herunterladen kommt? Datei von letzter Aktualisierung sichern
#get_upcoming_events Darstellungsfehler -> Ü
#Liste enthält keine Events ... prüfe ob überhaupt Events in der Liste sind, bevor Instanzierungen versucht wird ~l 128 Fehler beheben (fEventdur)

#Static Globals
ics_url = "https://stundenplanung.eah-jena.de/ical/raum/SPLUSF88401.ics" #ICS-Datei mit Belegungsdaten für Raum 03.03.33

textRoom = "Raum 03.03.33" # name zu static #Raumnummer Plan
staticTextNextEvent = 'nächste Veranstaltung:' #statischer text für nächste veranstaltung
staticTextTimeConnect = '-' # - verbindung zwischen uhrzeiten
staticTextFree = 'FREI' #Raum FREI
staticTextRefresh = 'zuletzt aktualisiert:' #statischer text zuletzt aktualisiert
staticTextCurrentEvent = 'aktuelle Veranstaltung:' #statischer text aktuelle Veranstaltung:
staticTextOccupied = 'BESETZT' #Raum BESETZT
staticTextNoEvent = 'Heute sind keine weiteren Veranstaltungen geplant!' #statischer text für Heute keine weiteren Veranstaltungen geplant! (fall 2 of free display)
staticTextNextEventAt = 'nächste Veranstaltung am:'
staticTextListEmpty = 'keine weiteren Veranstaltungen geplant!';

#Fontstyles
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font25 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 25) 
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35) 
font90 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)


def getics(): #Herunterladen und Speichern der ICS
    
    with req.get(ics_url, verify=False) as rq: #Zertifikatspfad statt False eintragen
        with open('room_03-03-33.ics', 'wb') as file:
            
            file.write(rq.content)
            file.close()


def readics(): #Lesen der ICS-Datei als iCalendar-Objekt und Rückgabe
    
    icalfile = open('room_03-03-33.ics')
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    return gcal


def getupcoming_events(gcal, currentdt): #Durchsucht die ics und gibt eine sortierte Liste mit Event-Dictionnaries zurück

    icsevents = list()

    for component in gcal.walk(): #Durchläuft den Kalender und sucht nach Events, speichert die Daten in Dictionnaries in eine Liste
        
        if component.name == "VEVENT": #Speichert die Komponenten eines Events in Variablen  
            
            startdt = component.get('dtstart').dt #Beginn    
            enddt = component.get('dtend').dt #Ende
            sdescrp = component.get('description')          
            s = sdescrp.split('\n')
            sdozent = s[0]
            ssets = s[1]
            seventname = s[2] #Darstellungsproblem mit dem Zeichen in der ics Ã -> Ü
            timestamp = startdt - currentdt #Zeitstempel
            eventdur = enddt - startdt #Eventdauer
                
            if(timestamp.total_seconds() > eventdur.total_seconds()*(-1) and timestamp.total_seconds() < 0):
                bStatus = True
            else:
                bStatus = False
            
            if(timestamp.total_seconds() > eventdur.total_seconds()*(-1)):
                icsevents.append({'eventname':seventname, 'Dozent':sdozent, 'Start':startdt,'Ende':enddt,
                'Sets':ssets, 'Belegt':bStatus, 'timestamp':timestamp.total_seconds(), 'Dauer':eventdur.total_seconds()})
        

    sorted(icsevents, key = lambda i: i['Start'])
    
    return icsevents

#def display_occupied(): 

#def display_upcoming_events():

#def display_no_events_today():

#def display_no_events_in_list():

def main():

    try:
        epd = epd5in83b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        time.sleep(1)

        while True:
            
            #Raumstatus True: belegt, False: frei
            bRoomstat = False 
            #Ruft aktuelle, lokale Zeit und Datum ab
            currentdt = datetime.datetime.today() 
            #Liest die ics in ein icalender-objekt
            gcal = readics() 
            #Liefert sortierte Liste der Events
            events = getupcoming_events(gcal, currentdt) 

            #prüft ob laut ics noch Events geplant sind
            if(len(events) == 0): 
                
                #Sicht 4 - Keine Veranstaltungen geplant
                epd.clear()
                layoutRoomOccupiedRedText.text((150, 180), staticTextListEmpty, fill = 0, font=font35)
                print("Keine Veranstaltungen geplant")
            
            else: 
                #Instanziere Variablen für das aktuelle/nächste Event-Objekt = erstes Element in der Eventliste
                fTimestamp = events[0]['timestamp'] #Zeitstempel zum Steuern der Bildschirmaktualisierung
                fEventdur = events[0]['Dauer'] #Event-Dauer zum Steuern der Bildschirmaktualisierung
                bRoomstat = events[0]['Belegt'] #Event-Status schaltet Raum auf frei oder belegt
                sProf = events[0]['Dozent']
                sSubject = events[0]['eventname']
                Startdt = events[0]['Start']
                Enddt = events[0]['Ende']

                #Instanziere Texte für das Display
                textEventProf = sProf #Veranstaltung Prof.
                textEventSubject = sSubject #Veranstaltung Fach
                textEventStart = Startdt.strftime('%H:%M') #'HH:MM' #Startzeit Event
                textEventEnd = Enddt.strftime('%H:%M') #'HH:MM' #Endzeit
                textEventDate = Startdt.strftime('%d.%m.%Y') #Datum aktuelles/nächstes Event
                textDate = currentdt.strftime('%d.%m.%Y') #Datum heutiger Tag Event
                textRefreshTime = currentdt.strftime('%H:%M') #Zeit zu der das Display zuletzt aktualisiert wurde 'HH:MM'

                #Sicht 1 -> Event läuft  
                if(bRoomstat == True):
                    
                    epd.clear()
                    imgRoomOccupied = Image.open(os.path.join(picdir, 'layout_Room_Occupied.bmp'))
                    layoutRoomOccupiedRed = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
                    
                    layoutRoomOccupied = ImageDraw.Draw(imgRoomOccupied)
                    layoutRoomOccupiedRedText = ImageDraw.Draw(layoutRoomOccupiedRed)  
                    
                    layoutRoomOccupied.text((41, 46), textRoom, fill = 'white', font=font35)
                    layoutRoomOccupied.text((400, 46), textDate, fill = 'white', font=font35)
                    layoutRoomOccupiedRedText.text((150, 180), staticTextOccupied, fill = 0, font=font90)
                    layoutRoomOccupied.text((25, 348), staticTextCurrentEvent, fill = 'white', font=font30)
                    layoutRoomOccupied.text((345, 345), textEventStart, fill = 'white', font=font35)
                    layoutRoomOccupied.text((440, 343), staticTextTimeConnect, fill = 'white', font=font35)
                    layoutRoomOccupied.text((460, 345), textEventEnd, fill = 'white', font=font35)
                    layoutRoomOccupied.line((25, 383, 545, 383), fill = 'white',width=4)
                    layoutRoomOccupied.text((25, 400), textEventSubject, fill = 'white',font=font25)
                    layoutRoomOccupied.text((25, 432), textEventProf, fill = 'white', font=font25)
                    
                    epd.display(epd.getbuffer(imgRoomOccupied), epd.getbuffer(layoutRoomOccupiedRed))

                    fsleep = fEventdur + fTimestamp
                    time.sleep(fsleep)
                    #Aktualisiert sich erst wieder, wenn das Event vorbei ist

                #Sicht 2 -> kein Event, nächstes Event noch am selben Tag
                elif(bRoomstat == False and currentdt.date() == Startdt.date()):
                    
                    epd.clear()
                    imgRoomFree = Image.open(os.path.join(picdir, 'layout_Room_Free.bmp'))
                    layoutRoomFree = ImageDraw.Draw(imgRoomFree)

                    layoutRoomFree.text((41, 46), textRoom, fill = 'black', font=font35)
                    layoutRoomFree.text((350, 25), textDate, fill = 'black', font=font30)
                    layoutRoomFree.text((350, 70), staticTextRefresh, fill = 'black', font=font25)
                    layoutRoomFree.text((564, 70), textRefreshTime, fill = 'black', font=font25)
                    layoutRoomFree.text((238, 180), staticTextFree, fill = 'black', font=font90)
                    layoutRoomFree.text((25, 348), staticTextNextEvent, fill = 'black', font=font30)
                    layoutRoomFree.text((345, 345), textEventStart, fill = 'black', font=font35)
                    layoutRoomFree.text((440, 343), staticTextTimeConnect, fill = 'black', font=font35)
                    layoutRoomFree.text((460, 345), textEventEnd, fill = 'black', font=font35)
                    layoutRoomFree.line((25, 383, 545, 383), fill = 'black', width=4)
                    layoutRoomFree.text((25, 400), textEventSubject, fill = 'black',font=font25)
                    layoutRoomFree.text((25, 432), textEventProf, fill = 'black', font=font25)
                
                    epd.displayblack(epd.getbuffer(imgRoomFree)) #Bild wird an Display gesendet
                    
                    fsleep = Startdt - currentdt
                    if(fsleep.total_seconds() > 3600):
                        time.sleep(3600)
                    else:
                        time.sleep(fsleep.total_seconds()) #Aktualisiere Display Zu Beginn des nächsten Events

                #Sicht 3 -> heute keine Events mehr
                else:
                    
                    epd.clear()
                    imgRoomFree = Image.open(os.path.join(picdir, 'layout_Room_Free.bmp'))
                    layoutRoomFreeRed = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
                    
                    layoutRoomFree = ImageDraw.Draw(imgRoomFree)
                    layoutRoomFreeRedText = ImageDraw.Draw(layoutRoomFreeRed)  
                    
                    layoutRoomFree.text((41, 46), textRoom, fill = 'black', font=font35)
                    layoutRoomFree.text((350, 25), textDate, fill = 'black', font=font30)
                    layoutRoomFree.text((350, 70), staticTextRefresh, fill = 'black', font=font25)
                    layoutRoomFree.text((564, 70), textRefreshTime, fill = 'black', font=font25)
                    layoutRoomFree.text((238, 180), staticTextFree, fill = 'black', font=font90)
                    layoutRoomFreeRedText.text((25, 348), staticTextNoEvent, fill = 0, font=font25)
                    layoutRoomFreeRedText.line((25, 380, 605, 380), fill = 0,width=4)
                    layoutRoomFree.text((25, 400), staticTextNextEventAt, fill = 'black',font=font25)
                    layoutRoomFree.text((335, 400), textEventDate, fill = 'black',font=font25)
                    layoutRoomFree.text((335, 432), textEventStart, fill = 'black',font=font25)
                    layoutRoomFree.text((405, 432), staticTextTimeConnect, fill = 'black',font=font25)
                    layoutRoomFree.text((420, 432), textEventEnd, fill = 'black', font=font25)

                    epd.display(epd.getbuffer(imgRoomFree), epd.getbuffer(layoutRoomFreeRed))
                    time.sleep(900) #Aktualisiert sich jeden Viertel Stunde
    



    except IOError as e:    #??
        logging.info(e)
    
    except KeyboardInterrupt:    #??
        logging.info("ctrl + c:")
        epd5in83b_V2.epdconfig.module_exit()
        exit()



getics() #Skript soll einmal pro Tag neugestartet werden
main() #anschließend soll dieses Skript laufe


#def check_roomstat(events): #prüft, ob gerade ein Event läuft
'''Diese Funktion würde den Index des laufenden Events zurückgegeben. 
Da get_upcoming_events eine sortierte Liste der Daten liefert, ist es nur relevant, 
ob das erste Event den Status "belegt raum" oder "nicht" enthält.'''
#und 
'''    
    for key,value in enumerate(events): 
        if(value['Belegt'] == True):
            i = events.index(value)
            bRoomstat = True
            break

        else:
            bRoomstat = False
    
    return bRoomstat
'''
