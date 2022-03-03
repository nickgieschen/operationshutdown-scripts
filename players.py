from csv import reader

from unidecode import unidecode

from BbRefPage import BbRefPage
from config import year


def normalize_name(s):
    return unidecode(s.strip().translate(str.maketrans("", "", ".,")))


abbr_to_team_name = {
    "BICK": "Big Inning Corn King",
    "Browns": "Three Finger Browns",
    "CLM": "Clement St. Massive",
    "FURI": "Baseball Furies",
    "Hooples": "Hoopleheads",
    "Idiots": "Dostoevskian Idiots",
    "KPAS": "Ken Phelps All Stars",
    "MENDOZA": "Mendoza Line",
    "MK": "Mike Kingery",
    "MM": "Maya's Mysteries",
    "Pchs": "Peaches",
    "QF": "Quantum Fastball",
    "SNK": "SNK Crushers",
    "TBH": "The Bad Hombres",
    "THP": "Tom Henky-Pankies",
    "Tag": "HeMissedTheTag",
    "VU&N": "The Velvet Underground & Niko Goodrum",
    "WB": "The Wonder Bats"
}


class PlayerBase:
    @property
    def normalized_name(self):
        return normalize_name(self.name)

    @property
    def to_array(self):
        return [value for _, value in vars(self).items()]

    def __str__(self):
        return str(self.__dict__)


class Player(PlayerBase):
    def __init__(self, name, real_team, pos, os_team, fantrax_id):
        self.fantrax_id = fantrax_id
        self.name = name
        self.real_team = real_team
        self.pos = pos
        self.os_team = os_team
        self.fantrax_url = "https://www.fantrax.com/newui/playerProfile.go?pId=" + fantrax_id.strip("*")


class MinLPlayer(PlayerBase):
    def __init__(self, name, recorded_team, os_team, bbref_url):
        # If the name is like Bip Roberts (SP, TOR) we get just Bip Roberts and plunk the other part into
        # recorded_team if recorded_team isn't given
        name_split = name.split("(")
        if (not recorded_team or recorded_team == "") and len(name_split) > 1:
            recorded_team = name_split[1]
            print(recorded_team)
        self.id = None
        self.name = name_split[0].strip()
        self.os_team = os_team
        self.recorded_team = recorded_team
        self.bbref_team = None
        self.rookie_year = None
        self.birth_year = None
        self.bbref_url = bbref_url

    def to_array(self):
        return [self.name, self.os_team, self.recorded_team, self.bbref_team, self.birth_year, self.rookie_year,
                self.bbref_url]

    @property
    def bbref_file_path(self):
        parts = self.bbref_url.split("=")
        if len(parts) > 1:
            return "data/" + year + "/bbref-pages/" + parts[1]
        else:
            parts = self.bbref_url.split("/")
            return "data/" + year + "/bbref-pages/" + parts[len(parts) - 1]

    @property
    def bbref_page(self):
        return BbRefPage(self.bbref_file_path)


class FantraxProspect(PlayerBase):
    def __init__(self, name, team, position, age, signing_year, signing_market):
        self.name = name
        self.team = team
        self.position = position
        self.age = age
        self.signing_year = signing_year
        self.signing_market = signing_market


def get_all_os_players():
    """ This represents all players in Fantrax, rostered or not"""
    players = []
    with open('data/2021-majl-owned-players.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader, None)
        list_of_rows = list(csv_reader)
        for row in list_of_rows:
            players.append(Player(row[1], row[2], row[3], abbr_to_team_name[row[5]], row[0]))
    return players


def get_all_os_rostered_players():
    """ This represents rostered players in Fantrax"""
    return [player for player in get_all_os_players() if player.os_team]


def get_minl_players_from_file():
    """ this represents a list of current minor league players"""
    players = []
    with open("data/" + year + "/minl-players.tsv", "r") as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        #next(csv_reader, None) # only if there is a header row
        list_of_rows = list(csv_reader)
        for row in list_of_rows:
            players.append(MinLPlayer(row[0],
                                      row[1] if 1 < len(row) else None,
                                      row[2] if 2 < len(row) else None,
                                      row[3] if 3 < len(row) else None))
    return players


def get_minl_players_maybe():
    """ This represents a list of current minor league players from which we want to filter out graduates"""
    players = []
    with open('data/minl-players-maybe.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader, None)
        list_of_rows = list(csv_reader)
        for row in list_of_rows:
            players.append(MinLPlayer(row[1], row[2], row[0], row[9]))
    return players


def get_fantrax_prospects():
    players = []
    with open('data/potential-minor-league-pick-list.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader, None)
        list_of_rows = list(csv_reader)
        for row in list_of_rows:
            players.append(FantraxProspect(row[0], row[1], row[2], row[10], row[15], row[16]))
    return players


def get_draft_results():
    """ Returns a dict of fantrax id to round """
    draft = {}
    with open('data/2021-majl-draft-results.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader, None)
        list_of_rows = list(csv_reader)
        for row in list_of_rows:
            draft[row[0]] = row[1]
    return draft
