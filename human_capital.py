import csv

import parsers
from nlp import analyse_text
from sec import SECSession

if __name__ == '__main__':
    sec = SECSession()
    with open("10k.csv", "r") as csv_file:
        entries = csv.DictReader(csv_file)
        for entry in entries:
            for year in [2022, 2021, 2020]:
                if not entry[f"{year}"]:
                    print(f"No 10-K of {entry['company_ticker']} for {year=}")
                    continue
                response = sec.get_filing(entry[f"{year}"])
                human_capital_section = getattr(parsers, entry["company_ticker"])(response)
                if human_capital_section:
                    analyse_text(human_capital_section, year, entry["company_ticker"])
