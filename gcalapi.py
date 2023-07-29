from __future__ import print_function

import datetime
from dateutil.tz import tzlocal
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Based on quickstart.py in https://developers.google.com/calendar/api/quickstart/python

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def gcal_access():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gcal_token.json'):
        creds = Credentials.from_authorized_user_file('gcal_token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gcal_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gcal_token.json', 'w') as token:
            token.write(creds.to_json())

    scheduleInfo = {}
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tzlocal()).isoformat()
        endofday = datetime.datetime.now(tzlocal()).replace(hour = 23, minute = 59, second = 59).isoformat()

        # Get list of calendar ID
        calList_result = service.calendarList().list().execute()
        calList = calList_result.get('items',[])
        calIDList = []
        for cl in calList:
            calIDList.append(cl['id'])
        #print(calIDList)

        events = []
        for cid in calIDList:
            events_result = service.events().list(calendarId=cid, timeMin=now, timeMax = endofday,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events.extend(events_result.get('items', []))

        if not events:
            print('No upcoming events found.')
            return {}
        

        
        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['start'].get('date'))
            #print(start, end, event['summary'])
            startTime = re.findall('T\d{2}:\d{2}', start)[0]
            endTime = re.findall('T\d{2}:\d{2}', end)[0]

            startHr = int(startTime[1:3])

            if(int(endTime[4:]) == 0):
                endHr = int(endTime[1:3]) - 1
            else:
                endHr = int(endTime[1:3])
            
            scheduleInfo[event['summary']] = (startHr, endHr)
    
        #print(scheduleInfo)

    except HttpError as error:
        print('An error occurred: %s' % error)
    
    return scheduleInfo


#gcal_access()