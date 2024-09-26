import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime 
import pandas as pd
from parse_game_link import format_error_json

GAME_LINKS_URL = "https://miacathletics.com/stats.aspx?path=baseball&year=2023"

def get_page(URL):
    try:
        response = requests.get(URL, headers={'User-Agent': 'Custom'})
        return bs(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error Processing URL: {URL}")
        _json = format_error_json("URL get", datetime.now(), URL, e)
        with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Error_logs.json", "a") as file:
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
        for tr in table.find_all("tr"):
            rows = tr.find_all("td")
            if rows:
                dates.append(rows[0].text)
                opponents.append(rows[1].text.strip().strip("* ").strip("at "))
                results.append(rows[2].text)
                links.append("https://miacathletics.com/" + rows[2].find("a")["href"])
        team_json = save_team_table_links_helper(team_name, team_record, links, dates, opponents, results)
        all_matches.append(team_json)
    full_json = {
        "All Games": all_matches
    }
    with open("C:\\Users\\jhurt\\OneDrive\\Desktop\\MIACDIII_Tracker\\logs\\Game_links.json", "a") as file:
        file.write(json.dumps(full_json, indent=4))

def save_team_table_links_helper(name, record, links, dates, opponents, results):
    matches_list = create_matches_json(links, dates, opponents, results)
    _json = {
        "Team":name,
        "Record": record,
        "Matches": matches_list
    }
    return _json
    
def create_matches_json(links, dates, opponents, results):
    matches_list = []
    for i in range(len(links)):
        match = {
            "Opponent": f"{opponents[i]}",
            "Date": f"{dates[i]}", 
            "Resuilt": f"{results[i]}", 
            "URL": f"{links[i]}" 
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