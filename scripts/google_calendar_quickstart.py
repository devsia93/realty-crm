"""Standalone Google Calendar quickstart / diagnostic (relocated from repo root).

This is NOT imported by the application. It is a developer-facing OAuth +
`googleapiclient` smoke script kept for reference and ad-hoc debugging. The
application's calendar seam lives at ``backend/integrations/calendar.py``
(``CalendarGateway`` + ``NullCalendarGateway``); nothing there calls Google yet.

Run from the REPO ROOT so the relative ``credentials.json`` / ``token.pickle``
paths resolve:

    python scripts/google_calendar_quickstart.py

Prerequisites (legacy dependency set, pinned in requirements.txt):
    google-api-python-client==1.12.8, google-auth-oauthlib==0.4.2,
    google-auth-httplib2==0.0.4, google-auth==1.27.0.

On first run it opens a browser for OAuth consent and caches a
``token.pickle``. To change scopes, delete ``token.pickle`` first.
"""
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.

    Prints the start and the name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()
