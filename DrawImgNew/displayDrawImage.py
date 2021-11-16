import logging
import time
from PIL import Image,ImageDraw,ImageFont


logging.basicConfig(level=logging.DEBUG)

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




logging.info("1.Drawing on the Horizontal image...") 

#HBlackimage = Image.new('1', (648, 480), 255)  # 648*480
#HRYimage = Image.new('1', (648, 480), 255)  # 648*480  HRYimage: red or yellow image  



font18 = ImageFont.truetype(('Font.ttc'), 18)
font25 = ImageFont.truetype(('Font.ttc'), 25)
font30 = ImageFont.truetype(('Font.ttc'), 30)
font35 = ImageFont.truetype(('Font.ttc'), 35)
font90 = ImageFont.truetype(('Font.ttc'), 90)


#Darstellung für den fall: Raum ist frei und am gleichen tag findet noch eine Veranstaltung statt
imgRoomFreeEventUpcoming = Image.open('layout_Room_Free.bmp')
layoutRoomFree = ImageDraw.Draw(imgRoomFreeEventUpcoming)

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

imgRoomFreeEventUpcoming.show()

time.sleep(2)

#Darstellung für den fall: Raum ist frei und am gleichen tag findet keine weitere Veranstaltung statt
imgRoomFreeNoEventUpcoming = Image.open('layout_Room_Free.bmp')
layoutRoomFree = ImageDraw.Draw(imgRoomFreeNoEventUpcoming)

layoutRoomFree.text((41, 46), textRoom, fill = 'black', font=font35)
layoutRoomFree.text((350, 25), textDate, fill = 'black', font=font30)
layoutRoomFree.text((350, 70), staticTextRefresh, fill = 'black', font=font25)
layoutRoomFree.text((564, 70), textRefreshTime, fill = 'black', font=font25)
layoutRoomFree.text((238, 180), staticTextFree, fill = 'black', font=font90)
layoutRoomFree.text((25, 348), staticTextNoEvent, fill = 'red', font=font25)
layoutRoomFree.line((25, 380, 605, 380), fill = 'red',width=4)
layoutRoomFree.text((25, 400), staticTextNextEventAt, fill = 'black',font=font25)
layoutRoomFree.text((335, 400), textNextEventDate, fill = 'black',font=font25)
layoutRoomFree.text((335, 432), textNextEventStart, fill = 'black',font=font25)
layoutRoomFree.text((405, 432), staticTextTimeConnect, fill = 'black',font=font25)
layoutRoomFree.text((420, 432), textNextEventEnd, fill = 'black', font=font25)

imgRoomFreeNoEventUpcoming.show()

time.sleep(2)

#Darstellugng für den fall: Raum ist Besetzt
imgRoomOccupied = Image.open('layout_Room_Occupied.bmp')
layoutRoomOccupied = ImageDraw.Draw(imgRoomOccupied)

layoutRoomOccupied.text((41, 46), textRoom, fill = 'white', font=font35)
layoutRoomOccupied.text((400, 46), textDate, fill = 'white', font=font35)
layoutRoomOccupied.text((150, 180), staticTextOccupied, fill = 'red', font=font90)
layoutRoomOccupied.text((25, 348), staticTextCurrentEvent, fill = 'white', font=font30)
layoutRoomOccupied.text((345, 345), textCurrentEventStart, fill = 'white', font=font35)
layoutRoomOccupied.text((440, 343), staticTextTimeConnect, fill = 'white', font=font35)
layoutRoomOccupied.text((460, 345), textCurrentEventEnd, fill = 'white', font=font35)
layoutRoomOccupied.line((25, 383, 545, 383), fill = 'white',width=4)
layoutRoomOccupied.text((25, 400), textCurrentEventSubject, fill = 'white',font=font25)
layoutRoomOccupied.text((25, 432), textCurrentEventProf, fill = 'white', font=font25)

imgRoomOccupied.show()
