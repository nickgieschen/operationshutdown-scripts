from csv import reader

from config import year


def get_submitted_keepers():
    """ This represents all players in Fantrax, rostered or not"""
    players = []
    with open(f"data/{year}/submitted-keepers.tsv", "r") as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        rows = list(csv_reader)
        teams = []
        for team in rows[0]:
            teams.append((team, []))
        for row in rows[1:]:
            for idx, player in enumerate(row):
                teams[idx][1].append(player or None)
        return teams


def get_keeper_rounds():
    with open(f"data/{year}/keeper_rounds.tsv", "r") as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        return list(csv_reader)[1:]


def get_minor_league_players():
    with open(f"data/{year}/minl-players.tsv", "r") as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        return list(csv_reader)


def check_keeper_round(player, team, proposed_round, keeper_rounds, minl_players):
    found = []
    for row in keeper_rounds:
        if row[0].strip() == player.strip() and row[3].strip() == team:
            found.append((player, row[3], row[5]))
        if len(found) == 0:
            # We check if in the minor league list
            for minl_player in minl_players:
                if minl_player[0] == player and minl_player[1] == team:
                    found.append((player, row[1], 24))
    if len(found) == 0:
        print(f"not found: {player} {team} {proposed_round}")
    if len(found) > 1:
        print(f"ambiguous:  {player} {team} {proposed_round}")
    for entry in found:
        if int(entry[2]) < int(proposed_round):
            print(f"bad round: {player} {team} {proposed_round}")


def check_keeper_rounds():
    submitted_keepers = get_submitted_keepers()
    keeper_rounds = get_keeper_rounds()
    minor_leagues_players = get_minor_league_players()
    for team, keepers in submitted_keepers:
        for inx, keeper in enumerate(keepers):
            if keeper:
                check_keeper_round(keeper, team, inx + 1, keeper_rounds, minor_leagues_players)


check_keeper_rounds()
