#!/usr/bin/env python
"""
  Download Ontario provincial COVID daily data
"""
from datetime import datetime
from pathlib import Path

import requests

DATADIR = Path("data")
URL = "https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv"


def main():
  """ Download provincial data
  """
  rv = requests.get(URL, stream=True)
  rv.raise_for_status()
  print(rv.headers)

  # grab YYYY-MM-DD from Etag (timestamp)
  sse = float(rv.headers["ETag"].replace('"',"").split("-")[0])
  date = datetime.fromtimestamp(sse).strftime("%Y-%m-%d")

  fname = DATADIR / Path(f"{date}-provincial-covid.csv")
  with open(fname, "w") as f:
    f.write(rv.text)


if __name__ == "__main__":
  main()