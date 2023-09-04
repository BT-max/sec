import csv

from sec import SECSession

if __name__ == '__main__':
    sec = SECSession(**{
        "dateRange": "custom", "category": "custom",
        "startdt": "2020-01-01", "enddt": "2022-12-31",
        "forms": ["10-K"]
    })
    # read the csv file
    data = []
    fields_name = ["company_name", "company_ticker", "entity_name", "company_cik", "2022", "2021", "2020"]
    with open('Russell 3000® Index - Constituents.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for index, row in enumerate(reader):
            company_name, company_ticker = row['company_name'], row['company_ticker']
            meta_data = sec.get_company_metadata(company_ticker=company_ticker)
            if not meta_data:
                meta_data = sec.get_company_metadata(company_name=company_name)
            entries = {
                "company_name": company_name,
                "company_ticker": company_ticker,
                "entity_name": meta_data.get("entity_name", ""),
                "company_cik": meta_data.get("company_cik", ""),
            }
            filling_urls = sec.get_filing_url(company_name=company_name, company_ticker=company_ticker)
            entries.update(filling_urls.get(company_ticker, {}))
            data.append(entries)

    with open('10k.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields_name)
        writer.writeheader()
        writer.writerows(data)
