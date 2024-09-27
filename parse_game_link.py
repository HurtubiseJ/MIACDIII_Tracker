import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime 
import pandas as pd
import os

URL = "https://miacathletics.com/boxscore.aspx?id=7ltyipP022aUJKmSgYVs3wXi7up73ghniwD5ElWyd07J7BNseBaMQePf0fY%2f3yUPU2iqzJuGrvibprNxltHfhjzahKugRChgIwJOnQuU36aPr6UCGn53aYCKiFnmHaPs9JDhc3iAafJNN0wdhpG5rEfXVis2ofyXQVlRHTsQbyA%3d&path=baseball"

#TODO: Maybe Remove
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

#Opens specified link and return etree html object
def get_page(URL):  
    try:
        page = requests.get(URL, headers={'User-Agent': 'Custom'})
        soup = bs(page.text, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error Processing URL: {URL}")
        if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Error_logs.json"):
            with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Error_logs.json", "w+") as f:
                pass
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Error_logs.json", "r+") as file:
            full_errors = json.load(file)
            _json = {}
            if full_errors == None: 
                _json = {"Errors": [{"date":f"{datetime.now()}", "URL":f"{URL}", "ErrorCode":f"{e}"}]}
            else:
                _json = format_error_json(full_errors, "URL get", datetime.now(), URL, e)
            file.write(json.dumps(_json, indent=4))

def format_error_json(full_list, date, URL, errorCode):
    full_list['Errors'].append({"date":f"{date}", "URL":f"{URL}", "ErrorCode":f"{errorCode}"})
    return full_list

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

def write_json(_json, URL):
    id = URL.split('id=')[1].split("%3d&path")[0]

    if not os.path.exists(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}"):
        os.mkdir(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}")
    with open(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}\\Game_Box.json", "w+") as file:
        file.write(json.dumps(_json, indent=4) + '\n')

#Function goes to the Box Score section of the given url and parses the given stats
def parse_and_store_box(soup, URL):
    try: 
        print(f"Processing Box scores for URL: {URL}")
        _json = get_all_box_stats_json(soup, URL)
        write_json(_json, URL)
        write_URL_to_logs_box(URL, True)
    except:
        print(f"Failed to parse box scores URL: {URL}")
        write_URL_to_logs_box(URL, False)

def parse_all(URL):
        print(f"Processing URL: {URL}")
        soup = get_page(URL)
        #Box Section
        parse_and_store_box(soup, URL)
        #play by play section
        parse_and_store_PBP(soup, URL)
        print(f'Finished Processing URL: {URL}')

def write_URL_to_logs_box(URL, isUpdated):
    if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json"):
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json", "w+") as f:
            pass
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json", "r+") as file:
            try:
                _json = ""
                try:
                    _json = json.load(file)
                    for game in _json['Logs']:
                        if game['URL'] == URL:
                            _json['URL']["lastUpdated"] = datetime.now()
                            _json['URL']["BoxisUpdated"] = isUpdated
                except:
                    _json = {"Logs": [{"URL": URL, "lastUpdated": str(datetime.now()), "BoxisUpdated": isUpdated, "PBPisUpdated": False}]}
                file.write(json.dumps(_json, indent=4))
            except: 
                print(f"Failed to modify update Box log for: {URL}")

def write_URL_to_logs_PBP(URL, isUpdated):
    if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json"):
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json", "w+") as f:
            pass
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\update_logs\\update_logs.json", "r+") as file:
            try:
                _json = ''
                try:
                    _json = json.load(file)
                    for game in _json['Logs']:
                        if game['URL'] == URL:
                            _json['URL']["lastUpdated"] = datetime.now()
                            _json['URL']["PBPisUpdated"] = isUpdated
                except:
                    _json = {"Logs": [{"URL": URL, "lastUpdated": str(datetime.now()), "BoxisUpdated": False, "PBPisUpdated": isUpdated}]}
                file.write(json.dumps(_json, indent=4))
            except: 
                print(f"Failed to modify update PBP log for: {URL}")
                
def get_all_box_stats_json(soup, URL):
    header = get_box_score_header(soup)
    box_tables = get_all_box_tables(soup)
    _json_batters = get_batter_tables(box_tables)
    _json_pitchers = get_pitcher_tables(box_tables)
    _json_team_box_totals = get_header_stats_totals(header)
    _json_box_details = get_header_details(header)
    _json_game = {
        "Game Stats":{
            "URL": URL,
            "Game Details":_json_box_details, 
            "Game Totals":_json_team_box_totals,
            "Batters":_json_batters, 
            "Pitchers":_json_pitchers
        }
    }
    return _json_game

def parse_and_store_PBP(soup, URL):
    try:
        tables = get_all_play_tables(soup)
        outcomes = []
        for i in range(len(tables)):
            inning_outcome = []
            for th in tables[i].find_all("th"):
                if th.text == 'Play Description':
                    continue 
                inning_outcome.append(th.text)
            outcomes.append(inning_outcome)
        game_descriptions_dict = parse_outcomes(outcomes, URL)
        id = URL.split('id=')[1].split("%3d&path")[0]
        if not os.path.exists(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}"):
            os.mkdir(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}")
        with open(f"C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\GAMES\\{id}\\Game_PBP.json", 'w+') as file:
            file.write(json.dumps(game_descriptions_dict, indent=4))
    except:
        write_URL_to_logs_PBP(URL, False)


#Output Json object {name, hittype, hit location}
name_regex = r".?\.?\s?[A-Za-z]+" #USE SEARCH 
hittype_regex = r'\b(?:doubled|singled|tripled|flied|popped up|lined out|grounded out|grounded into double play|walked|struck out|homered|hit by pitch|bunt|sacrifice fly|sacrifice bunt|intentionally walked|hit a home run|up the middle)\b'
hitlocation_regex = r'\b(?:cf|rf|lf|1b|2b|3b|ss|c|p|to p|center field|right field|left field|first base|second base|third base|shortstop|catcher|pitcher|center|third|first|second)\b'
abrivs = {"to p": 1, "p": 1, "c": 2, "1b": 3, "2b": 4, "3b": 5, "ss": 6, "lf": 7, "cf": 8, "rf": 9, "pitcher": 1, "catcher": 2, "first base": 3, "second base": 4, "third base": 5, "shortstop": 6, "left field": 7, "center field": 8, "right field": 9, "center": 10, "third": 11, "first": 12, "second": 13}

def parse_outcomes(outcomes, URL):
    game_outcomes = []
    missed_lines = []
    for i in range(len(outcomes)):
        inning = []
        for j in range(len(outcomes[i])):
            name = re.search(name_regex, outcomes[i][j])
            hit_type = re.search(hittype_regex, outcomes[i][j])
            hitlocation = re.search(hitlocation_regex, outcomes[i][j])
            if name != None and hitlocation != None:
                inning.append({"Name" : name.group(), "Hit type": hit_type.group() if hit_type else "N/A" , "Hit location": abrivs[hitlocation.group()]})
            else:
                missed_lines.append(outcomes[i][j] + '\n')
        curr_inning = (i // 2) + 1
        inning_json = {f"inning {curr_inning}": inning}
        game_outcomes.append(inning_json)
    if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\missed_PBP_lines.txt"):
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\missed_PBP_lines.txt", "w+") as f:
            pass
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\missed_PBP_lines.txt", "r+") as file:
        for line in missed_lines:
            file.write(line)
    outcomes_dict = {"URL": URL, "Game Details" : game_outcomes}
    return outcomes_dict

def main():
    parse_all(URL)

if __name__ == "__main__":
    main()