import json
import re
from difflib import SequenceMatcher

import requests
from tenacity import retry, stop_after_attempt, wait_random


class SECSession:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.93 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8',
        'referer': 'https://www.sec.gov/edgar/search/',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    cookies = {}
    payload = {}
    session = requests.Session()
    url = "https://efts.sec.gov/LATEST/search-index"

    def get_filing(self, link):
        return self.session.get(link, headers=self.headers)

    @staticmethod
    def _validate_payload(**kwargs):
        valid_kwargs = {"category", "startdt", "enddt", "forms", "dateRange"}
        for field_name, _ in kwargs.items():
            if field_name not in valid_kwargs:
                raise RuntimeError(f"Invalid payload {field_name}")

    def _clean_payload(self):
        self.payload.pop("entityName", None)
        self.payload.pop("ciks", None)
        self.payload.pop("from", None)
        self.payload.pop("page", None)

    def __init__(self, **kwargs):
        self._validate_payload(**kwargs)
        self.cookies = self.session.get(self.url, headers=self.headers).cookies.get_dict()
        self.payload = kwargs

    @retry(stop=stop_after_attempt(7), wait=wait_random(min=0.5, max=2), reraise=True)
    def get_company_metadata(self, company_ticker="", company_cik="", company_name=""):
        details = {}
        search_term = company_cik or company_ticker or company_name
        response = self.session.post(
            self.url,
            json={"keysTyped": search_term},
            headers=self.headers,
            cookies=self.cookies,
        )
        response_data = json.loads(response.text)
        if not response_data["hits"]["total"]["value"]:
            return details
        for company_details in response_data["hits"]["hits"]:
            if company_details["_source"].get("tickers", ""):
                tickers = company_details["_source"]["tickers"].replace(" ", "").replace("-", ".").split(",")
            else:
                tickers = []
            if tickers and company_ticker not in tickers:
                continue
            if not tickers and \
                    SequenceMatcher(
                        None, company_name.lower(),
                        company_details["_source"].get("entity_words", "").lower()
                    ).ratio() < 0.5:
                continue
            details = {
                "entity_name": company_details["_source"]["entity_words"],
                "company_cik": company_details["_id"].zfill(10),
            }
            if tickers:
                details["company_ticker"] = tickers
            break
        return details

    @staticmethod
    def _update_data(company_details):
        data = {}
        data_source = company_details['_source']
        company_cik = re.sub("^0+(?!$)", "", company_details['_source']['ciks'][-1])
        file_name = re.sub(r"(?<=\d)-(?=\d)", "", company_details['_id']).replace(':', '/')
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{company_cik}/{file_name}"
        try:
            data[data_source["file_date"].split("-")[0]] = "|".join([
                data[data_source["file_date"].split("-")[0]], filing_url
            ])
        except (KeyError, TypeError):
            data[data_source["file_date"].split("-")[0]] = filing_url
        return data

    @retry(stop=stop_after_attempt(7), wait=wait_random(min=0.5, max=2), reraise=True)
    def get_filing_url(self, company_name="", company_ticker=""):
        data = {}
        if company_name and company_ticker:
            company_metadata = self.get_company_metadata(company_ticker=company_ticker)
            if not company_metadata:
                company_metadata = self.get_company_metadata(company_name=company_name)
            if not company_metadata:
                return {f"{company_ticker}": {}}
                # raise RuntimeError(f"Unable to find company {company_name=} {company_ticker=}")
            entity_name, company_cik = company_metadata["entity_name"], company_metadata["company_cik"]
            self._clean_payload()
            self.payload.update({
                "entityName": entity_name,
                "ciks": [f"{company_cik}"],
            })
            data = {f"{company_ticker}": {}}
        page = 1
        offset = 0
        response_data = {"hits": {"total": {"value": 1}}}
        while offset < response_data['hits']['total']['value']:
            if offset > 0:
                self.payload.update({
                    "from": offset,
                    "page": page,
                })
            response = self.session.post(
                self.url,
                json=self.payload,
                cookies=self.cookies,
                headers=self.headers,
            )
            response_data = json.loads(response.text)
            if 'error' in response_data or 'hits' not in response_data:
                raise RuntimeError(f"Unable to parse {response_data=}")
            if not response_data['hits']['hits']:
                data[company_ticker] = {"2022": "", "2021": "", "2020": ""}
            for company_details in response_data['hits']['hits']:
                data[company_ticker].update(self._update_data(company_details))
            page += 1
            offset += len(response_data['hits']['hits'])
        return data


if __name__ == '__main__':
    sec = SECSession(**{
        "dateRange": "custom", "category": "custom",
        "startdt": "2020-01-01", "enddt": "2022-12-31",
        "forms": ["10-K"]
    })
    print(sec.get_filing_url(company_name="ALPHABET CLASS A", company_ticker="GOOGL"))
