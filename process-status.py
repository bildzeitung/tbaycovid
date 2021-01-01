#!/usr/bin/env python
"""
  Process Health Unit Case by Status COVID data
"""

from pathlib import Path

import matplotlib
import matplotlib.pylab as plt

matplotlib.use("Agg")
import seaborn as sns
import pandas as pd

DATADIR = Path("data")
GRAPHDIR = Path("graphs")
HEALTH_UNITS = {
    "NORTHWESTERN": "NWHU",
    "THUNDER BAY DISTRICT": "TBDHU",
}


def get_data():
    """Choose latest data file"""
    fnames = sorted(x for x in DATADIR.glob("*case-by-status.csv"))
    latest = fnames[-1]
    date = "-".join(latest.name.split("-")[0:3])
    print(f"Latest file: {latest}")
    return open(latest), date


def make_by_day(frame, filedate, unit):
    """Create a graph of new cases by earliest incident date"""
    gb = frame.set_index("FILE_DATE").resample("D").last().fillna(0).reset_index()
    max_date = gb["FILE_DATE"].max().strftime("%Y-%m-%d")
    gb["resolved_by_delta"] = gb["RESOLVED_CASES"].diff().fillna(0).astype(int)
    gb["deaths_delta"] = gb["DEATHS"].diff().fillna(0).astype(int)
    print(gb)
    ax = sns.lineplot(
        data=gb, x="FILE_DATE", y="ACTIVE_CASES", linewidth=1
    )
    ax = sns.lineplot(data=gb, x="FILE_DATE", y="resolved_by_delta", linewidth=1)
    ax = sns.lineplot(data=gb, x="FILE_DATE", y="deaths_delta", linewidth=1)
    ax.set(
        ylabel="# of cases",
        xlabel="Date",
        title=f"{unit} Case Counts by Day ({max_date})",
    )

    plt.legend(["active", "resolved", "deaths"])
    plt.gcf().autofmt_xdate()
    ax.figure.savefig(GRAPHDIR / Path(f"{filedate}-case-count-by-date.png"))


def process_health_unit(unit, filedate, frame):
    frame = frame.query(f"PHU_NAME=='{unit}'").copy()

    frame["FILE_DATE"] = pd.to_datetime(
        frame["FILE_DATE"], format="%Y%m%d"
    )

    # reports ..
    reports = (make_by_day,)
    for r in reports:
        r(frame, f"{unit.lower().replace(' ', '-')}-{filedate}", HEALTH_UNITS[unit])
        plt.clf()


def main():
    sns.set_theme()
    sns.set(rc={'figure.figsize':(15,6)})
    data, filedate = get_data()
    frame = pd.read_csv(data)

    for h in HEALTH_UNITS:
        process_health_unit(h, filedate, frame)


if __name__ == "__main__":
    main()
