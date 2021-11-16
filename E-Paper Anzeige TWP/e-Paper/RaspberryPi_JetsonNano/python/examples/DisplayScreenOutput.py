#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd5in83b_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd5in83b_V2 Demo")
    
    epd = epd5in83b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)


    #allgemeine Texte
    textRoom = 'Raum: 03.33.33' #Raumnummer Plan
    textDate = '20.12.2022' #Datum Heutiger Tag
    staticTextNextEvent = 'nächste Veranstaltung:' #statischer text für nächste veranstaltung
    staticTextTimeConnect = '-' # - verbindung zwischen uhrzeiten

    #allgemeine zusatztexte/variablen für event free
    textNextEventProf = 'Prof. Dr. Erfurth' #Nächste Veranstaltung Prof.
    textNextEventSubject = 'WI/EC Obj. Orient. Programmierung' #Nächste Veranstaltung Fach
    textNextEventStart = '17:00' #Startzeit des nächsten events
    textNextEventEnd = '20:00' #Endzeit des nächsten events
    staticTextFree = 'FREI' #Raum FREI
    staticTextRefresh = 'zuletzt aktualisiert:' #statischer text zuletzt aktualisiert
    textRefreshTime = '20:05' #Zeit zu der das Display zuletzt aktualisiert wurde

    #zusatztexte/variablen für event free (ausschließlich für kein weirteres event am gleichen Tag)
    staticTextNoEvent = 'Heute sind keine weiteren Veranstaltungen geplant!' #statischer text für Heute keine weiteren Veranstaltungen geplant! (fall 2 of free display)
    staticTextNextEventAt = 'nächste Veranstaltung am:'
    textNextEventDate = '22.12.2022'

    #zusatztexte für event occupied
    staticTextCurrentEvent = 'aktuelle Veranstaltung:' #statischer text aktuelle Veranstaltung:
    textCurrentEventProf = 'Prof. Dr. Erfurth' #aktuelle Veranstaltung Prof.
    textCurrentEventSubject = 'WI/EC Obj. Orient. Programmierung' #aktuelle Veranstaltung Fach
    textCurrentEventStart = '17:00' #Startzeit der aktuellen Veranstaltung
    textCurrentEventEnd = '20:00' #Endzeit der aktuellen Veranstaltung
    staticTextOccupied = 'BESETZT' #Raum BESETZT

    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font25 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 25) 
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35) 
    font90 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
    
    
    
    
    
    
    imgRoomFree = Image.open(os.path.join(picdir, 'layout_Room_Free.bmp'))
    layoutRoomFree = ImageDraw.Draw(imgRoomFree)
        
    layoutRoomFree.text((41, 46), textRoom, fill = 'black', font=font35)
    layoutRoomFree.text((350, 25), textDate, fill = 'black', font=font30)
    layoutRoomFree.text((350, 70), staticTextRefresh, fill = 'black', font=font25)
    layoutRoomFree.text((564, 70), textRefreshTime, fill = 'black', font=font25)
    layoutRoomFree.text((238, 180), staticTextFree, fill = 'black', font=font90)
    layoutRoomFree.text((25, 348), staticTextNextEvent, fill = 'black', font=font30)
    layoutRoomFree.text((345, 345), textNextEventStart, fill = 'black', font=font35)
    layoutRoomFree.text((440, 343), staticTextTimeConnect, fill = 'black', font=font35)
    layoutRoomFree.text((460, 345), textNextEventEnd, fill = 'black', font=font35)
    layoutRoomFree.line((25, 383, 545, 383), fill = 'black', width=4)
    layoutRoomFree.text((25, 400), textNextEventSubject, fill = 'black',font=font25)
    layoutRoomFree.text((25, 432), textNextEventProf, fill = 'black', font=font25)
        
    epd.displayblack(epd.getbuffer(imgRoomFree)) #Bild wird an Display gesendet
    
    time.sleep(5)
    
    
    imgRoomOccupied = Image.open(os.path.join(picdir, 'layout_Room_Occupied.bmp'))
    layoutRoomOccupiedRed = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    
    
    layoutRoomOccupied = ImageDraw.Draw(imgRoomOccupied)
    layoutRoomOccupiedRedText = ImageDraw.Draw(layoutRoomOccupiedRed)  
      
    
    layoutRoomOccupied.text((41, 46), textRoom, fill = 'white', font=font35)
    layoutRoomOccupied.text((400, 46), textDate, fill = 'white', font=font35)
    layoutRoomOccupiedRedText.text((150, 180), staticTextOccupied, fill = 0, font=font90)
    layoutRoomOccupied.text((25, 348), staticTextCurrentEvent, fill = 'white', font=font30)
    layoutRoomOccupied.text((345, 345), textCurrentEventStart, fill = 'white', font=font35)
    layoutRoomOccupied.text((440, 343), staticTextTimeConnect, fill = 'white', font=font35)
    layoutRoomOccupied.text((460, 345), textCurrentEventEnd, fill = 'white', font=font35)
    layoutRoomOccupied.line((25, 383, 545, 383), fill = 'white',width=4)
    layoutRoomOccupied.text((25, 400), textCurrentEventSubject, fill = 'white',font=font25)
    layoutRoomOccupied.text((25, 432), textCurrentEventProf, fill = 'white', font=font25)
      
    epd.display(epd.getbuffer(imgRoomOccupied), epd.getbuffer(layoutRoomOccupiedRed))
    
    time.sleep(5)
    
    
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
    layoutRoomFree.text((335, 400), textNextEventDate, fill = 'black',font=font25)
    layoutRoomFree.text((335, 432), textNextEventStart, fill = 'black',font=font25)
    layoutRoomFree.text((405, 432), staticTextTimeConnect, fill = 'black',font=font25)
    layoutRoomFree.text((420, 432), textNextEventEnd, fill = 'black', font=font25)

    epd.display(epd.getbuffer(imgRoomFree), epd.getbuffer(layoutRoomFreeRed))
    
    '''
    logging.info("Clear...")
    #epd.init()
    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
    '''   
       
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd5in83b_V2.epdconfig.module_exit()
    exit()

