#!/usr/bin/env python
"""
  Post daily travel advisories
"""
import json
import twitter

from pathlib import Path
from types import SimpleNamespace

import json


DATADIR = Path("data-travel")
CHUNKS = 3


def main():
    latest = sorted(x for x in DATADIR.glob("*.jl"))[-1]
    with open(latest) as f:
        data = [json.loads(x)["fragment"] for x in f]

    def chunks():
        for i in range(0, len(data), CHUNKS):
            yield data[i : i + CHUNKS]

    all_chunks = [c for c in chunks()]
    l = len(all_chunks)
    tweets = []
    for x, c in enumerate(all_chunks):
        f = "\n".join(c)
        s = f"[{x+1}/{l}] Flights with potential COVID exposure:\n{f}\n@TBDHealthUnit  @CityThunderBay"
        tweets.append(s)

    # tweet the graphs
    with Path("twitter.json").open() as f:
        keys = SimpleNamespace(**json.load(f))
    api = twitter.Api(
        consumer_key=keys.api_key,
        consumer_secret=keys.api_secret_key,
        access_token_key=keys.access_token,
        access_token_secret=keys.access_token_secret,
    )

    reply_to = 0
    for t in tweets:
        r = api.PostUpdate(t, in_reply_to_status_id=reply_to)
        reply_to = r.id


if __name__ == "__main__":
    main()
