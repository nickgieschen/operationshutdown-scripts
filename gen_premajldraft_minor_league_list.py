"""
Set config/year

Generating beginning of the year minor league list
    - Create a tsv in data/[year]/prev-year-minl-players.tsv with no header row (see data-exmaples/minl-players)
    - We insert the players into the db with insert_minl_players_from_file
    - We run the current list through get bbref_urls so each minor leaguer has a bbref url
    - We run that list through get_bbref_pages so each minor leaguer has a bbref page
    - We run that through get_rookie_status, get_bbref_team, and get_birth_year to fill in the player's data
    - We run output_preseason_list
"""
import csv
import time
import traceback
import urllib.request
from os.path import exists

from duckduckgo_search import ddg

from BbRefPage import BbRefPage
from config import year
from db import conn
from players import get_minl_players_maybe, get_all_os_players, get_fantrax_prospects, get_minl_players_from_file, \
    get_all_os_rostered_players, MinLPlayer


def search_for_player_url(name, team):
    # team_name = team if team is not None else ""
    urls = ddg(f'site:baseball-reference.com {name}', max_results=1)
    if len(urls) > 0:
        time.sleep(10)
        return urls[0]["href"]


def to_tsv(file_name, data, folder="out"):
    with open(folder + "/" + year + "/" + file_name, 'w', newline='') as csvfile_out:
        writer = csv.writer(csvfile_out, delimiter='\t')
        for row in data:
            writer.writerow(row)


def generate_list_with_maybe_graduated_players():
    """ Reads from current list of minor league players and identifies players who have graduated by matching against the list of all players in Fantrax"""
    result = []
    all_os_players = get_all_os_players()
    for minlg_player in get_minl_players_maybe():
        potential_matches = []
        for os_player in all_os_players:
            if os_player.normalized_name == minlg_player.normalized_name:
                potential_matches.append(os_player)
        result.append((minlg_player, potential_matches))

    out = []
    for res in result:
        out.append(res[0].to_array)
        for potential_match in res[1]:
            out.append([None, *potential_match.to_array])

    to_tsv("minor-league-teams.tsv")


def generate_pick_list():
    """ Reads from Fantrax prospect list and identifies players who are taken by matching against the current minor
    league list and current rostered players list """
    result = []
    min_and_maj_players = [*get_all_os_rostered_players(), *get_minl_players_from_file()]
    for prospect in get_fantrax_prospects():
        potential_matches = []
        for rostered_player in min_and_maj_players:
            if prospect.normalized_name == rostered_player.normalized_name:
                potential_matches.append(rostered_player)
        result.append((prospect, potential_matches))
    out = []
    for res in result:
        out.append(res[0].to_array)
        for potential_match in res[1]:
            out.append([None, *potential_match.to_array])

    to_tsv("pick-list.tsv", out)


def sqlize(val):
    return str.replace(val, "'", "''")


def insert_minl_players_from_file():
    players = get_minl_players_from_file()
    for player in players:
        sql = f"insert into minor_league_players (name, os_team, recorded_majl_team, bbref_url, year) values ('{sqlize(player.name)}', '{sqlize(player.os_team)}', '{player.recorded_team}', '{sqlize(player.bbref_url)}', {year}) "
        print(sql)
        conn.execute(sql)
    conn.commit()
    cursor = conn.execute("select count(*) from minor_league_players")
    print("rows in file " + str(len(players)))
    print("rows inserted " + str(cursor.fetchone()[0]))
    conn.close()


def get_minor_league_players_from_db():
    cursor = conn.execute(f"select * from minor_league_players where year = {year}")
    players = []
    for row in cursor:
        player = MinLPlayer(row[0], row[2], row[1], row[4])
        player.id = row[8]
        player.bbref_team = row[3]
        player.rookie_year = row[5]
        player.birth_year = row[6]
        players.append(player)
    return players


def get_bbref_urls():
    players = get_minor_league_players_from_db()
    # if there's no bbref id, we find one
    for player in players:
        try:
            if not player.bbref_url:
                url = search_for_player_url(player.name, None)
                conn.execute(f"UPDATE minor_league_players set bbref_url = '{sqlize(url)}' where ID = {player.id}")
                conn.commit()
                print("processed " + player.name)
        except Exception as e:
            print(player.name)
            print(traceback.format_exc())


def get_bbref_pages():
    players = get_minor_league_players_from_db()
    for player in players:
        if player.bbref_url:
            try:
                if not exists(player.bbref_file_path):
                    opener = urllib.request.FancyURLopener({})
                    f = opener.open(player.bbref_url)
                    content = f.read()
                    nf = open(player.bbref_file_path, "wb")
                    nf.write(content)
                    nf.close()
                    print("Got file for " + player.name)
                    time.sleep(5)
            except Exception as e:
                print("Exception handling " + player.bbref_url)
                # print(traceback.format_exc())
    for player in players:
        if not exists(player.bbref_file_path):
            print("Missing file for " + player.name)


def get_rookie_status():
    players = get_minor_league_players_from_db()
    for player in players:
        if player.bbref_url:
            try:
                rookie_year = player.bbref_page.year_exceeded_rookie_status
                if rookie_year:
                    conn.execute(f"UPDATE minor_league_players set rookie_year = '{rookie_year}' where ID = {player.id}")
                    conn.commit()
            except Exception as e:
                print(e)
                print("Error getting rookie year for " + player.name)


def get_bbref_team():
    players = get_minor_league_players_from_db()
    for player in players:
        if player.bbref_url:
            try:
                bbref_team = player.bbref_page.mlb_team
                if bbref_team:
                    conn.execute(f"UPDATE minor_league_players set bbref_majl_team = '{bbref_team}' where ID = {player.id}")
                    conn.commit()
            except Exception as e:
                print(e)
                print("Error getting bbref team for " + player.name)


def get_birth_year():
    players = get_minor_league_players_from_db()
    for player in players:
        if player.bbref_url:
            try:
                birth_year = player.bbref_page.birth_date
                if birth_year:
                    conn.execute(f"UPDATE minor_league_players set birth_year = '{birth_year.year}' where ID = {player.id}")
                    conn.commit()
            except Exception as e:
                print(e)
                print("Error getting birth year for " + player.name)


def output_preseason_list():
    players = get_minor_league_players_from_db()
    out = []
    for player in players:
        out.append(player.to_array())
    to_tsv(year + "-minl-players.tsv", out, folder="out")


# generate_list_with_maybe_graduated_players()
# generate_pick_list()


# insert_minl_players_from_file()
# get_bbref_urls()
# get_bbref_pages()
# get_rookie_status()
# get_bbref_team()
# get_birth_year()
# output_preseason_list()

