import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime 
import pandas as pd

URL = "https://miacathletics.com/boxscore.aspx?id=7ltyipP022aUJKmSgYVs3wXi7up73ghniwD5ElWyd07J7BNseBaMQePf0fY%2f3yUPGBOMQ6HzAX3wcEsySnJXko%2bkFOoKQSSLBvhfpeT0ohBQdoC2HNEJUUesGkojIIgiZkhCjY0oOJdfJAONgjhmArcWEHU7ce2nyu2T%2bM%2f8lU7kEfD%2f%2f9ZmPM1hfHeK2jhw&path=baseball"

#Opens specified link and return etree html object
def get_page(URL):  
    try:
        page = requests.get(URL, headers={'User-Agent': 'Custom'})
        soup = bs(page.text, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error Processing URL: {URL}")
        _json = format_error_json("URL get", datetime.now(), URL, e)
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Error_logs.json", "a") as file:
            file.write(json.dumps(_json, indent=4))

def format_error_json(date, URL, errorCode):
    return {"date":f"{date}", "URL":f"{URL}", "ErrorCode":f"{errorCode}"}

def get_box_score_section(soup):
    return soup.find('section', id='box-score')

def get_play_by_play_section(soup):
    return soup.find('section', id='play-by-play')

def get_all_play_tables(soup):
    play_section = get_play_by_play_section(soup)
    all_innings = play_section.find('div', id='inning-all')
    return all_innings.find_all('table')

def get_all_box_tables(soup):
    box_score_section = get_box_score_section(soup)
    return box_score_section.find_all("table")

def get_box_score_header(soup):
    return soup.find('header', class_="sidearm-box-score-header row")

def get_header_stats_totals(header):
    table = header.find('table')
    df = pd.read_html(table.prettify())[0]
    teams = df["Team"].tolist()
    runs = df["R"].tolist()
    hits = df['H'].tolist()
    errors = df["E"].tolist()
    team_stats = [
        {
            "Team": teams[0],
            "R": runs[0],
            "H": hits[0],
            "E": errors[0]
        },
        {
            "Team": teams[1],
            "R": runs[1],
            "H": hits[1],
            "E": errors[1]
        }
    ]
    return {"Team totals": team_stats}

def get_header_details(header):
    aside = header.find('aside', class_='game-details')
    dl = aside.find('dl')
    date = dl.find('dt', text="Date").find_next_sibling('dd').text
    start = dl.find('dt', text="Start").find_next_sibling('dd').text
    Time = dl.find('dt', text="Time").find_next_sibling('dd').text
    location = dl.find('dt', text="Site").find_next_sibling('dd').text
    return {"Date":f"{date}", "Start":f"{start}", "Time":f"{Time}", "Site":f"{location}"}


def parse_header(header):
    get_header_details(header)
    _json = {"Game details": get_header_details(header), "Team totals": get_header_stats_totals(header)}
    return json.dumps(_json, indent=4)

def main():
    soup = get_page(URL)
    header = get_box_score_header(soup)
    box_tables = get_all_box_tables(soup)
    play_tables = get_all_play_tables(soup)
    team_box_stats = parse_header(header)
    print(team_box_stats)
    # print(len(play_tables))
    # print(header)

if __name__ == "__main__":
    main()