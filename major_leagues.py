from minor_leagues import to_tsv
from players import get_all_os_rostered_players, get_draft_results


def generate_keeper_list():
    """For this we need
        1. [year]-majl-draft-results.csv (the results of the draft which includes the round each player was drafted)
        2. [year]-majl-owned-players.csv (the end of year owned players)
    """
    next_years_round = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6, 12: 7, 13: 7, 14: 8, 15: 9,
                        16: 10, 17: 10, 18: 11, 19: 12, 20: 13, 21: 17, 22: 17, 23: 17, 24: 17}
    out = []
    rostered_players = get_all_os_rostered_players()
    draft = get_draft_results()
    for player in rostered_players:
        previous_year_round = draft.get(player.fantrax_id)
        next_year_round = next_years_round[int(previous_year_round)] if previous_year_round else 24
        out.append([*player.to_array, next_year_round])

    out.sort(key=lambda r: r[6])
    out.sort(key=lambda r: r[4])
    #print(out)
    to_tsv("2021_keepers.tsv", out)


generate_keeper_list()
