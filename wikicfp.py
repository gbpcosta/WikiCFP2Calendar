import feedparser
import urllib
from bs4 import BeautifulSoup
from datetime import datetime
import time

class WikiCFPParser(object):
    categories = None
    last_update = NotImplemented
    feed_url = 'http://www.wikicfp.com/cfp/rss?cat=%s'

    def __init__(self, categories):
        self.categories = categories
        # TODO: include last_update (read from file)

    def prepareCategory(self, category):
        return category.lower().replace(' ', '%20')

    def parseFeed(self, verbose = 0):
        for category in self.categories:
            feed = feedparser.parse(self.feed_url % self.prepareCategory(category))

            # TODO: Check if it was updated (compare previous update date to d.updated ou d.updated_parsed)

            events = []
            n_entries = len(feed.entries)
            for ii, entry in enumerate(feed.entries):
                if verbose > 0:
                    print "Processing entry %d / %d from the %s category" % (ii+1, n_entries, category.capitalize())

                title = entry.title_detail.value.split(' : ')[0] # Acronym
                description = entry.summary # Full description
                link = entry.link # URL

                conf_page_data = urllib.urlopen(link) # capture page data using URL to WikiCFP page of the conference

                soup = BeautifulSoup(conf_page_data, "html.parser")

                table = soup.body.find_all('table', attrs={'class': 'gglu'})[0] # Select table with important dates and where the event will occur
                tds = table.find_all('td')
                dates_text = "Important information:\n" # text that will be included in the event description
                for jj, tp in enumerate(table.find_all('th')):
                    dates_text = dates_text + "\t" + tp.text.strip() + ": " + tds[jj].text.strip() + "\n"

                    if tp.text.strip().lower() == "submission deadline":
                        deadline = datetime.strptime(tds[jj].text.strip(), '%b %d, %Y') # Deadline will be used as event date
                    if tp.text.strip().lower() == "where":
                        location = tds[jj].text.strip() # Location will be used in event

                categories_table = soup.body.find_all('table', attrs={'class': 'gglu'})[1]
                keywords = categories_table.find_all('a')[1:]
                keywords_list = []
                keywords_text = "Keywords:\n"
                for keyword in keywords:
                    keywords_list.append(keyword.text.capitalize())
                    keywords_text = keywords_text + "\t" + keyword.text.capitalize() + "\n"

                final_description = description + "\n\n" + dates_text + "\n" + keywords_text

                event = {'summary': title,
                        'description': final_description,
                        'location': location,
                        'start': {
                            'date': deadline.strftime("%Y-%m-%d")
                            },
                        'end': {
                            'date': deadline.strftime("%Y-%m-%d")
                            }#,
                        # 'endTimeUnspecified': True,
                        # 'anyoneCanAddSelf': True,
                        # 'guestsCanInviteOthers': True,
                        # 'guestsCanModify': True,
                        # 'reminders': {
                        #     'useDefault': True
                        #     }
                        }

                if datetime.today().date() < deadline.date() and event not in events:
                    # print deadline.strftime("%b %d, %Y")
                    events.append(event)

                time.sleep(5) # WikiCFP requested that, at most, one query was issued every five seconds
            events = sorted(events, key = lambda tup: tup['start']['date'])

        return events
