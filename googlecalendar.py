import os
import datetime
from httplib2 import Http

from apiclient import discovery
from oauth2client import file, client, tools

class GoogleCalendar(object):
    calendar = None
    client_secret_file = None
    flags = None

    # TODO: modify constants
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    APPLICATION_NAME = 'WikiCFP 2 Google Calendar'

    def __init__(self, calendar='primary', client_secret_file = 'client_secret.json', flags = None):
        self.calendar = calendar
        self.client_secret_file = client_secret_file
        self.flags = flags

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'wikicfp2calendar.json')

        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def listCalendars(self):
        credentials = self.get_credentials()
        http = credentials.authorize(Http())
        service = discovery.build('calendar', 'v3', http=http)

        page_token = None
        while True:
          calendar_list = service.calendarList().list(pageToken=page_token).execute()
          for calendar_list_entry in calendar_list['items']:
            print "%s : %s" % (calendar_list_entry['summary'], calendar_list_entry['id'])
          page_token = calendar_list.get('nextPageToken')
          if not page_token:
            break

    def setCalendar(self, calendar):
        self.calendar = calendar

    # TODO: verify if event was update, and update the calendar event if necessary
    def checkEvent(self, service, event):
        events_q = service.events().list(calendarId=self.calendar, maxResults=1, q=event['summary']).execute() # using summary as a primary key
        return len(events_q.get('items', []))

    def includeEvents(self, events, verbose=0):
        credentials = self.get_credentials()
        http = credentials.authorize(Http())
        service = discovery.build('calendar', 'v3', http=http)

        for event in events:
            if not self.checkEvent(service, event):
                event = service.events().insert(calendarId=self.calendar, sendNotifications=True, body=event).execute()
                if verbose > 0:
                    print 'Event created: %s (%s)' % (event.get('summary'), event.get('htmlLink'))
