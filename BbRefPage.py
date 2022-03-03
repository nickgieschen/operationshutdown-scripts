import re
from datetime import datetime

from bs4 import BeautifulSoup


class BbRefPage:

    def __init__(self, file):
        self.file = file
        self._parsed_data = None

    @property
    def has_data(self):
        return self.data is not None

    @property
    def data(self):
        if self.file is not None:
            if self._parsed_data is None:
                f = open(self.file, "r")
                self._parsed_data = BeautifulSoup(f, 'lxml')
            return self._parsed_data

    @property
    def mlb_team(self):
        if self.data is not None:
            team_el = self.data.find(id="meta").find("strong", string="Team:")
            if team_el is not None:
                return team_el.next_sibling.next_sibling.get_text().strip()

    @property
    def year_exceeded_rookie_status(self):
        if self.data is not None:
            rookie_status_el = self.data.find(id="meta").find("strong", string="Rookie Status:")
            if rookie_status_el:
                rookie_status = rookie_status_el.parent.get_text().strip()
                if "Still Intact" in rookie_status:
                    return None
                return int(re.search(r"\d{4}", rookie_status).group())

    @property
    def draft_info(self):
        if self.data is not None:
            el = self.data.find(id="meta").find("strong", string="Draft")
            if el is not None:
                return el.parent.get_text().strip()

    @property
    def career_ab(self):
        sb = self.data.find(id="standard_batting")
        if sb is None:
            return None
        mlb = sb.find("tfoot").find("tr", {"class": "mlb"})
        if mlb is None:
            return None
        return int(mlb.find("td", {"data-stat": "AB"}).get_text())

    @property
    def career_ip(self):
        sb = self.data.find(id="standard_pitching")
        if sb is None:
            return None
        mlb = sb.find("tfoot").find("tr", {"class": "mlb"})
        if mlb is None:
            return None
        return float(mlb.find("td", {"data-stat": "IP"}).get_text())

    @property
    def birth_date(self):
        return datetime.strptime(self.data.find(itemprop="birthDate")["data-birth"], "%Y-%m-%d")

    @property
    def name(self):
        return self.data.find(itemtype="https://schema.org/Person").find(itemprop="name").get_text()

    @property
    def did_exceed_rookie_status(self):
        return self.year_exceeded_rookie_status is not None
