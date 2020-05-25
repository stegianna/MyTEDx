import requests
from bs4 import BeautifulSoup



def extractSource(url):
    return requests.get(url).text



def extract_event_data(url):
    dict = {}
    soup = BeautifulSoup(extractSource(url), "html.parser")
    event = soup.find('div', {'class':'tedx-events-table'}) \
        .find('tr', {'class': 'tedx-events-table__event tedx-events-table__event--current'})
    event_rows = event.find_all('td',{'class':'table__cell'})
    event_date = str(event_rows[0].contents[2])
    event_loc = str(event_rows[2].contents[2])
    dict["event_date"] = event_date
    dict["event_loc"] = event_loc
    return dict