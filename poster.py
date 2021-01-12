#!/usr/bin/env python
"""
  Post daily graph
"""
import dateparser
import json
import twitter

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from fetch import grab_all

from process import process_reports
from process_status import process_status

HEALTH_UNITS = {
    "@CityThunderBay": "thunder-bay",
    "Northwestern Health Unit": "northwestern",
}


def main():
    # retrieve data files & make sure they're for today
    as_at_dates = grab_all()
    now = datetime.now().date()
    assets = []
    for d, n, f in as_at_dates:
        print(f"Checking {d} [{f}]")
        data_date = dateparser.parse(d).date()
        assert data_date == now, f"Stats not ready yet: {now} vs {data_date}"
        if n == "case-by-status":
            assets.extend(process_status(open(f), now))
        if n == "provincial-covid":
            assets.extend(process_reports(open(f), now))

    indent = "\n\t"
    print(f"Assets:{indent}{indent.join([str(x) for x in assets])}")

    # tweet the graphs
    with Path("twitter.json").open() as f:
        keys = SimpleNamespace(**json.load(f))
    api = twitter.Api(
        consumer_key=keys.api_key,
        consumer_secret=keys.api_secret_key,
        access_token_key=keys.access_token,
        access_token_secret=keys.access_token_secret,
    )

    for d, h in HEALTH_UNITS.items():
        print(f"Uploading assets for {h}...")
        ids = []
        for x in assets:
            if h not in str(x):
                continue
            ids.append(api.UploadMediaSimple(open(x, "rb")))
        api.PostUpdate(
            f"Daily #COVID19 Update for {d}. Graphs show active cases, by age, and counts by episode date #COVID19Ontario",
            media=ids,
        )


if __name__ == "__main__":
    main()
