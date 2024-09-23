import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime 
import pandas as pd

URL = "https://miacathletics.com/boxscore.aspx?id=7ltyipP022aUJKmSgYVs3wXi7up73ghniwD5ElWyd07J7BNseBaMQePf0fY%2f3yUPGBOMQ6HzAX3wcEsySnJXko%2bkFOoKQSSLBvhfpeT0ohBQdoC2HNEJUUesGkojIIgiZkhCjY0oOJdfJAONgjhmArcWEHU7ce2nyu2T%2bM%2f8lU7kEfD%2f%2f9ZmPM1hfHeK2jhw&path=baseball"

#TODO: Maybe Remove
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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

def get_batter_tables(box_tables):
    #tables 3 and 4, 1 indexed
    table1 = box_tables[2]
    table2 = box_tables[3]
    df1 = pd.read_html(table1.prettify())[0].fillna(-1)
    df2 = pd.read_html(table2.prettify())[0].fillna(-1)
    return {"Team 1 Batting": df1.to_dict("records"), "Team 2 Batting": df2.to_dict("records")}

def get_pitcher_tables(box_tables):
    #tables 5 6, 1 indexed
    table1 = box_tables[4]
    table2 = box_tables[5]
    df1 = pd.read_html(table1.prettify())[0].fillna(-1)
    df2 = pd.read_html(table2.prettify())[0].fillna(-1)
    return {"Team 1 Pitching": df1.to_dict('records'), "Team 2 Pitching": df2.to_dict("records")}

def write_json(_json):
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Game_stats.json", "a") as file:
        file.write(json.dumps(_json, indent=4) + '\n')

#Function goes to the Box Score section of the given url and parses the given stats
#Game Details
#Game Totals
#Batters
#Pitchers
def parse_and_store_box(URL):
    try: 
        print(f"Processing URL: {URL}")
        soup = get_page(URL)
        _json = get_all_box_stats_json(soup)
        write_json(_json)
        write_URL_to_logs(URL, True)
    except:
        print(f"Failed to parse URL: {URL}")
        write_URL_to_logs(URL, False)

def write_URL_to_logs(URL, isUpdated):
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\update_logs.json", "r+") as file:
            try:
                _json = json.load(file)
                for game in _json:
                    if game['URL'] == URL:
                        _json['URL']["lastUpdated"] = datetime.now()
                        _json['URL']["isUpdated"] = isUpdated
            except: 
                _json_element = {"URL": URL, "lastUpdated": str(datetime.now()), "isUpdated": isUpdated}
                file.write(json.dumps(_json_element, indent=4) + '\n')
                

def get_all_box_stats_json(soup):
    header = get_box_score_header(soup)
    box_tables = get_all_box_tables(soup)
    _json_batters = get_batter_tables(box_tables)
    _json_pitchers = get_pitcher_tables(box_tables)
    _json_team_box_totals = get_header_stats_totals(header)
    _json_box_details = get_header_details(header)
    _json_game = {
        "Game Stats":{
            "Game Details":_json_box_details, 
            "Game Totals":_json_team_box_totals,
            "Batters":_json_batters, 
            "Pitchers":_json_pitchers
        }
    }
    return _json_game

# def parse_and_store_play(URL):

    

def main():
    parse_and_store_box(URL)

#To get team box stats json call get_box_score_header(soup)
#then pass to parse_header()

if __name__ == "__main__":
    main()