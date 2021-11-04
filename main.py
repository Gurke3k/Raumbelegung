from datetime import datetime, timedelta, timezone, date
import icalendar
from dateutil.rrule import *
import json

data = {}

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

icalfile = open('calendar\SPLUSF88401_TZ_Berlin.ics', 'rb')
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
        
    
icalfile.close()