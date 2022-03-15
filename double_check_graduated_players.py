from csv import reader

from config import year


def get_minor_league_graduates():
    with open(f"data/{year}/minl-players.tsv", "r") as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        return [(p[1], p[0]) for p in list(csv_reader) if p[4]][1:]


def get_submitted_keepers():
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


def double_check_graduated_players():
    keepers = dict(get_submitted_keepers())
    graduates = get_minor_league_graduates()
    unkept = graduates[:]
    for team, player in graduates:
        if team in keepers:
            if player in keepers[team]:
                unkept.remove((team, player))
        else:
            print(f"team not checked: {team}")
    print(unkept)


double_check_graduated_players()


