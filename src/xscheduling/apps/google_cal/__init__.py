# -*- coding: utf-8 -*-
try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time
from datetime import datetime

def client_login(email, password):
  calendar_service = gdata.calendar.service.CalendarService()
  calendar_service.email = email
  calendar_service.password = password
  calendar_service.source = 'Google-Calendar_Python_Sample-1.0'
  calendar_service.ProgrammaticLogin()
  return calendar_service

def insert_single_event(calendar_service, title='Sample Title', 
                      content='Sample content', where='Somewhere', 
                      start_time=None, end_time=None, href=None):
    event = gdata.calendar.CalendarEventEntry()
    event.title = atom.Title(text=title)
    event.content = atom.Content(text=content)
    event.where.append(gdata.calendar.Where(value_string=where))

    if start_time:
      start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    if end_time:
      end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    if start_time is None:
      # Use current time for the start_time and have the event last 1 hour
      start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
      end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))      
    event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
    
    if href:
      new_event = calendar_service.InsertEvent(event, href)
    else:
      new_event = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')
    
    return new_event


def get_all_events(calendar_service):
  feed = calendar_service.GetCalendarEventFeed()
  events = []
  for an_event in feed.entry:
    title = an_event.title.text
    content =  an_event.content.text
    all_day = False
    event = dict(id=an_event.id.text, title=title)
    for a_when in an_event.when:
      start = a_when.start_time
      end = a_when.end_time
      if start.find('T') < 0:
        start = datetime.strptime(start, '%Y-%m-%d')
#        end = datetime.strptime(end, '%Y-%m-%d')
        all_day = True
      else:
        start = datetime.strptime(start[:19], '%Y-%m-%dT%H:%M:%S')
        end = datetime.strptime(end[:19], '%Y-%m-%dT%H:%M:%S')
        event['end'] = end.ctime()
      event['start'] = start.ctime()
    event['allDay'] = all_day
    events.append(event)
  return events




