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

logging.basicConfig(level=logging.DEBUG)

#Programmbeschreibung
#Exception falls es zu einem Fehler beim Herunterladen kommt? Datei von letzter Aktualisierung sichern
#get_upcoming_events Darstellungsfehler -> Ü
#Liste enthält keine Events ... prüfe ob überhaupt Events in der Liste sind, bevor Instanzierungen versucht wird ~l 128 Fehler beheben (fEventdur)

#Static Globals
ics_url = "https://stundenplanung.eah-jena.de/ical/raum/SPLUSF88401.ics" #ICS-Datei mit Belegungsdaten für Raum 03.03.33

staticTextRoom = "Raum 03.03.33" # name zu static #Raumnummer Plan
staticTextNextEvent = 'nächste Veranstaltung:' #statischer text für nächste veranstaltung
staticTextTimeConnect = '-' # - verbindung zwischen uhrzeiten
staticTextFree = 'FREI' #Raum FREI
staticTextRefresh = 'zuletzt aktualisiert:' #statischer text zuletzt aktualisiert
staticTextCurrentEvent = 'aktuelle Veranstaltung:' #statischer text aktuelle Veranstaltung:
staticTextOccupied = 'BESETZT' #Raum BESETZT
staticTextNoEvent = 'Heute sind keine weiteren Veranstaltungen geplant!' #statischer text für Heute keine weiteren Veranstaltungen geplant! (fall 2 of free display)
staticTextNextEventAt = 'nächste Veranstaltung am:'
staticTextListEmpty1 = 'keine weiteren';
staticTextListEmpty2 = 'Veranstaltungen geplant!';

#Fontstyles
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font25 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 25) 
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35) 
font90 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)

''' Funktionen zum Behandeln von wiederkehrenden Events
def parse_recurrences(recur_rule, start, exclusions): 
    
    """ Find all reoccuring events """
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    now = datetime.now(timezone.utc)
    this_year = now + timedelta(days=60)
    dates = []
    for rule in rules.between(now, this_year):
        dates.append(rule.strftime("%D %H:%M"))
    return dates

def parse_events_with_recurrences()
    
    icalfile = open('', 'rb') #Hier Dateipfad zur Ics setzen
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            description = component.get('description')
            location = component.get('location')
            startdt = component.get('dtstart').dt
            enddt = component.get('dtend').dt
            exdate = component.get('exdate')

            if component.get('rrule'):
                reoccur = component.get('rrule').to_ical().decode('utf-8')
                for item in parse_recurrences(reoccur, startdt, exdate):
                    print("{0} bis {1}: {2}\n".format(item, summary, description, location))
                
            else:
                print("{0} bis {1}\n{3}\n".format(startdt.strftime("%d/%m/%y %H:%M"), enddt.strftime("%d/%m/%y %H:%M"), summary, description, location))   
'''
#Herunterladen und Speichern der ICS
def getics(): 
    
    with req.get(ics_url, verify=False) as rq: #Zertifikatspfad statt False eintragen
        with open('room_03-03-33.ics', 'wb') as file:
            file.write(rq.content)
            file.close()
#Lesen der ICS-Datei als iCalendar-Objekt
def readics(): 
    
    icalfile = open('room_03-03-33.ics')
    gcal = icalendar.Calendar.from_ical(icalfile.read())
    return gcal
#Durchsucht die ics und gibt eine sortierte Liste mit Event-Dictionnaries zurück
def get_upcoming_events(gcal, Currentdt): 
    
    icsevents = list()
    
    for component in gcal.walk(): #Durchläuft den Kalender und sucht nach Events, speichert die Daten in Dictionnaries in eine Liste
        
        if component.name == "VEVENT": #Speichert die Komponenten eines Events in Variablen  
            
            Startdt = component.get('dtstart').dt #Event-Beginn    
            Enddt = component.get('dtend').dt #Event-Ende
            sDescrp = component.get('description')        
            sDescrp = sDescrp.split('\n')
            sProf = sDescrp[0]
            sSets = sDescrp[1]
            sEventname = sDescrp[2] #Darstellungsproblem mit dem Zeichen in der ics Ã -> Ü
               
            tdeltaTimestamp = Startdt - Currentdt #Zeitstempel
            tdeltaEventdur = Enddt - Startdt #Eventdauer
               
            if(tdeltaTimestamp.total_seconds() > tdeltaEventdur.total_seconds()*(-1) and tdeltaTimestamp.total_seconds() < 0):
                bStatus = True
            else:
                bStatus = False
            
            if(tdeltaTimestamp.total_seconds() > tdeltaEventdur.total_seconds()*(-1)):
                icsevents.append({'eventname':sEventname, 'profname':sProf, 'starttime':Startdt,'endtime':Enddt,
                'sets':sSets, 'roomstatus':bStatus, 'timestamp':tdeltaTimestamp.total_seconds(), 'eventduration':tdeltaEventdur.total_seconds()})
        

    sorted(icsevents, key = lambda i: i['starttime']) #Sortiert die Liste anhand der Starttermine in aufsteigender Reihenfolge
    
    return icsevents

def getEpd():
    epd = epd5in83b_V2.EPD()

#Sicht 1 -> Display schaltet: Raum besetzt
def display_occupied(textDate,textEventStart,textEventEnd,textEventSubject,textEventProf): 

    epd = epd5in83b_V2.EPD()
    epd.Clear()
    imgRoomOccupied = Image.open(os.path.join(picdir, 'layout_Room_Occupied.bmp'))
    layoutRoomOccupiedRed = Image.new('1', (epd.width, epd.height), 255)  # 255: Clear the frame
                    
    layoutRoomOccupied = ImageDraw.Draw(imgRoomOccupied)
    layoutRoomOccupiedRedText = ImageDraw.Draw(layoutRoomOccupiedRed)  
                    
    layoutRoomOccupied.text((41, 46), staticTextRoom, fill = 'white', font=font35)
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
#Sicht 2 -> Display schaltet: Kein Event, nächstes Event noch am selben Tag
def display_upcoming_events(textDate,textRefreshTime,textEventStart,textEventEnd,textEventSubject,textEventProf): 
    
    epd = epd5in83b_V2.EPD()
    epd.Clear()
    imgRoomFree = Image.open(os.path.join(picdir, 'layout_Room_Free.bmp'))
    layoutRoomFree = ImageDraw.Draw(imgRoomFree)

    layoutRoomFree.text((41, 46), staticTextRoom, fill = 'black', font=font35)
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
#Sicht 3 -> Display schaltet: Heute keine Events mehr
def display_no_events_today(textDate,textRefreshTime,textEventDate,textEventStart,textEventEnd):
    
    epd = epd5in83b_V2.EPD()
    epd.Clear()
    imgRoomFree = Image.open(os.path.join(picdir, 'layout_Room_Free.bmp'))
    layoutRoomFreeRed = Image.new('1', (epd.width, epd.height), 255)  # 255: Clear the frame
                    
    layoutRoomFree = ImageDraw.Draw(imgRoomFree)
    layoutRoomFreeRedText = ImageDraw.Draw(layoutRoomFreeRed)  
                    
    layoutRoomFree.text((41, 46), staticTextRoom, fill = 'black', font=font35)
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
#Sicht 4 - Display schaltet: Keine Veranstaltungen geplant
def display_no_events_in_list(): 
    
    epd = epd5in83b_V2.EPD()
    epd.Clear()
    layoutNoEventsFound = Image.new('1', (epd.width, epd.height), 255)  # 255: Clear the frame
    layoutNoEventsFoundText = ImageDraw.Draw(layoutNoEventsFound)
                
    layoutNoEventsFoundText.text((200, 180), staticTextListEmpty1, fill = 0, font=font35)
    layoutNoEventsFoundText.text((125, 220), staticTextListEmpty2, fill = 0, font=font35)
                
    epd.displayblack(epd.getbuffer(layoutNoEventsFound))
    print("Keine Veranstaltungen geplant")
    time.sleep(3600)
#Main Funktion
def main():

    try:
        #Initialisere Display
        epd = epd5in83b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        time.sleep(1)

        while True:
            
            #Raumstatus True: belegt, False: frei
            bRoomstatus = False 
            #Ruft aktuelle, lokale Zeit und Datum ab
            Currentdt = datetime.datetime.today() 
            #Liest die ics in ein icalender-objekt
            gcal = readics() 
            #Liefert sortierte Liste der Events
            events = get_upcoming_events(gcal, Currentdt) 

            #prüfe, ob Liste Leer ist
            if(len(events) == 0): 
                #Sicht 4 - Keine Veranstaltungen geplant
                display_no_events_in_list() 
            
            else:
                #Initialisiere Variablen für das aktuelle/nächste Event-Objekt = erstes Element in der Eventliste
                fTimestamp = events[0]['timestamp'] #Zeitstempel zum Steuern der Bildschirmaktualisierung
                bRoomstatusus = events[0]['roomstatus'] #Event-Status schaltet Raum auf frei oder belegt
                
                sProf = events[0]['profname']
                sSubject = events[0]['eventname']
                Startdt = events[0]['starttime']
                Enddt = events[0]['endtime']

                #Initlisiere Texte für das Display
                textEventProf = sProf #Veranstaltung Prof.
                textEventSubject = sSubject #Veranstaltung Fach
                textEventStart = Startdt.strftime('%H:%M') #'HH:MM' #Startzeit Event
                textEventEnd = Enddt.strftime('%H:%M') #'HH:MM' #Endzeit
                textEventDate = Startdt.strftime('%d.%m.%Y') #Datum aktuelles/nächstes Event
                textDate = Currentdt.strftime('%d.%m.%Y') #Datum heutiger Tag Event
                textRefreshTime = Currentdt.strftime('%H:%M') #Zeit zu der das Display zuletzt aktualisiert wurde 'HH:MM'

                if(bRoomstatus == True):
                    #Sicht 1 - Raum besetzt
                    display_occupied(textDate,textEventStart,textEventEnd,textEventSubject,textEventProf)
                    fsleep = fEventdur + fTimestamp
                    time.sleep(fsleep) #Aktualisiert sich erst wieder, wenn das Event vorbei ist

                elif(bRoomstatus == False and Currentdt.date() == Startdt.date()):
                    #Sicht 2 -> kein Event, nächstes Event noch am selben Tag
                    display_upcoming_events(textDate,textRefreshTime,textEventStart,textEventEnd,textEventSubject,textEventProf)
                    
                    fsleep = Startdt - Currentdt
                    if(fsleep.total_seconds() > 3600):
                        time.sleep(3600)
                    else:
                        time.sleep(fsleep.total_seconds()) #Aktualisiere Display Zu Beginn des nächsten Events
                
                else:
                    #Sicht 3 -> heute keine Events mehr
                    display_no_events_today(textDate,textRefreshTime,textEventDate,textEventStart,textEventEnd)
                    time.sleep(3600) #Aktualisiert sich jeden Viertel Stunde
    
    except IOError as e:    #??
        logging.info(e)
    
    except KeyboardInterrupt:    #??
        logging.info("ctrl + c:")
        epd5in83b_V2.epdconfig.module_exit()
        exit()


#Funktionsaufruf
getics()
main()
