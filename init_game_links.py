import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime 
import pandas as pd
from parse_game_link import format_error_json
import os

GAME_LINKS_URL = "https://miacathletics.com/stats.aspx?path=baseball&year=2023"

def get_page(URL):
    try:
        response = requests.get(URL, headers={'User-Agent': 'Custom'})
        return bs(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error Processing URL: {URL}")
        _json = format_error_json("URL get", datetime.now(), URL, e)
        if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\Error_logs.json"):
            with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\Error_logs.json", "w+") as f:
                pass
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\Error_logs\\Error_logs.json", "r+") as file:
            curr_errors = json.load(file)
            curr_errors
            file.write(json.dumps(_json, indent=4))


#TODO: Merge links list and pandas table, decide what to move to JSON/Store
def save_team_table_links(teams, tables):
    all_matches = []
    for i in range(len(teams)):
        team_name = teams[i].text.split()[0]
        team_record = teams[i].text.split()[1].strip("(").strip(",")
        table = tables[i]
        links = []
        dates = []
        opponents = []
        results = []
        ids = []
        for tr in table.find_all("tr"):
            rows = tr.find_all("td")
            if rows:
                dates.append(rows[0].text)
                opponents.append(rows[1].text.strip().strip("* ").strip("at "))
                results.append(rows[2].text)
                link = rows[2].find("a")['href']
                links.append("https://miacathletics.com/" + link)
                id = link.split('id=')[1].split("%3d&path")[0]
                ids.append(id)

        team_json = save_team_table_links_helper(team_name, team_record, links, dates, opponents, results, ids)
        all_matches.append(team_json)
    full_json = {
        "All Games": all_matches
    }
    if not os.path.exists("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\MASTER_GAME_LINKS\\Game_links.json"):
            with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\MASTER_GAME_LINKS\\Game_links.json", "w+") as f:
                pass
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIAC_INFO\\MASTER_GAME_LINKS\\Game_links.json", "r+") as file:
        file.write(json.dumps(full_json, indent=4))

def save_team_table_links_helper(name, record, links, dates, opponents, results, ids):
    matches_list = create_matches_json(links, dates, opponents, results, ids)
    _json = {
        "Team":name,
        "Record": record,
        "Matches": matches_list
    }
    return _json
    
def create_matches_json(links, dates, opponents, results, ids):
    matches_list = []
    for i in range(len(links)):
        match = {
            "Opponent": f"{opponents[i]}",
            "Date": f"{dates[i]}", 
            "Resuilt": f"{results[i]}", 
            "URL": f"{links[i]}",
            "Id": f"{ids[i]}"
        }
        matches_list.append(match)
    return matches_list

#Returns a list of teams names and list of tables, teams[i] and tables[i] correlate 
def find_team_links_tables(soup):
    section = soup.find('section', id='by_team')
    return section.find_all('h5'), section.find_all('table')

def main():
    soup = get_page(GAME_LINKS_URL)
    teams, tables = find_team_links_tables(soup)
    save_team_table_links(teams, tables)

if __name__ == "__main__":
    main()