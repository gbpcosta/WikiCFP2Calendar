from googlecalendar import GoogleCalendar
from wikicfp import WikiCFPParser
import argparse
import json
from oauth2client import tools

def main():
  # parser = argparse.ArgumentParser(description='WikiCFP 2 Calendar: create Google calendar events based on CFPs from WikiCFP. \n\n Remember change config.json to contain your information.')
  # parser.add_argument('-l', '--listCalendars', action="store_true", default=False, help='Lists all available calendars and their identifiers.')
  # parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')
  # parser.add_argument('-v', '--verbose', type=int, action='count', default=0, help='Increase output verbosity.')
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

  with open('config.json') as config_file:
    config = json.load(config_file)

  if config['listCalendars']:
    # TODO: option to list calendars and help create config.json
    # cal = GoogleCalendar(client_secret=client_secret)
    print "Teste"
  else:
    # Get info from WikiCFP (This takes a while since only one query can be made every 5 seconds)
    cfp = WikiCFPParser(config['categories'])
    events = cfp.parseFeed(config['verbose'])

    # Create calendar events
    cal = GoogleCalendar(config['calendar'], config['client_secret_file'], flags)
    cal.includeEvents(events, verbose=config['verbose'])

if __name__ == '__main__':
  main()
