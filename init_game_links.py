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
    for i in range(len(teams)):
        team_name = teams[i].text.split()[0]
        team_record = teams[i].text.split()[1]
        table = tables[i]
        links = []
        for a in table.find_all("a", href=True):
            links.append(a['href'])



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