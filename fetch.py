#!/usr/bin/env python
"""
  Download Ontario provincial COVID daily data
"""
from datetime import datetime
from pathlib import Path

import requests

DATADIR = Path("data")
URLS = (
  ("https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv", "provincial-covid"),
  ("https://data.ontario.ca/dataset/1115d5fe-dd84-4c69-b5ed-05bf0c0a0ff9/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc/download/cases_by_status_and_phu.csv", "case-by-status"),
)


def grab(url, name):
    """Download provincial data"""
    rv = requests.get(url, stream=True)
    rv.raise_for_status()
    print(rv.headers['Last-Modified'])

    # grab YYYY-MM-DD from Etag (timestamp)
    sse = float(rv.headers["ETag"].replace('"', "").split("-")[0])
    date = datetime.fromtimestamp(sse).strftime("%Y-%m-%d")

    fname = DATADIR / Path(f"{date}-{name}.csv")
    with open(fname, "w") as f:
        f.write(rv.text)


def main():
  for url, name in URLS:
    grab(url, name)


if __name__ == "__main__":
    main()
