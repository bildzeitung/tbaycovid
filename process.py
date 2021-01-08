#!/usr/bin/env python
"""
  Process Ontario provincial COVID daily data
"""
from itertools import chain
from pathlib import Path

import matplotlib
import matplotlib.pylab as plt
import matplotlib.ticker as ticker

matplotlib.use("Agg")
import seaborn as sns
import pandas as pd
from pandas.api.types import CategoricalDtype

DATADIR = Path("data")
GRAPHDIR = Path("graphs")
WINDOW = 5
AGE_CATEGORIES = ("<20", "20s", "30s", "40s", "50s", "60s", "70s", "80s", "90s")
HEALTH_UNITS = {
    "Northwestern Health Unit": "NWHU",
    "Thunder Bay District Health Unit": "TBDHU",
}


def get_data():
    """Choose latest data file"""
    fnames = sorted(x for x in DATADIR.glob("*provincial-covid.csv"))
    latest = fnames[-1]
    date = "-".join(latest.name.split("-")[0:3])
    print(f"Latest file: {latest}")
    return open(latest), date


def make_by_age(frame, filedate, unit):
    """Active cases, grouped by age"""
    q = frame.query("Outcome1 == 'Not Resolved'")
    gb = q.groupby("byAge", as_index=False).agg(
        patients=pd.NamedAgg(column="byAge", aggfunc="size")
    )
    print(gb)
    max_date = q["Accurate_Episode_Date"].max().strftime("%Y-%m-%d")

    # make the graph
    ax = sns.barplot(data=gb, palette="Blues_d", y="patients", x="byAge")
    ax.set(
        xlabel="Age Group",
        ylabel="Active Cases",
        title=f"{unit} Active Cases by Age Group ({max_date})",
    )
    fname = GRAPHDIR / Path(f"{filedate}-by-age.png")
    ax.figure.savefig(fname)
    return fname


def make_cumulative(frame, filedate, unit):
    """Create a cumulative graph of cases over time"""
    gb = frame.groupby("Accurate_Episode_Date").agg(patients=("Row_ID", "count"))
    gb = gb.resample("D").last().fillna(0).reset_index()
    max_date = gb["Accurate_Episode_Date"].max().strftime("%Y-%m-%d")
    gb["cumulative"] = gb.patients.cumsum().astype(int)
    print(gb)
    print(gb.info())
    ax = sns.lineplot(
        data=gb, x="Accurate_Episode_Date", y="cumulative", linewidth=2, color="red"
    )
    ax.set(
        ylabel="Cumulative case count",
        xlabel="Date",
        title=f"{unit} Cumulative Cases by Episode Date ({max_date})",
    )
    ax2 = plt.twinx()
    sns.lineplot(
        data=gb, x="Accurate_Episode_Date", y="patients", ax=ax2, linewidth=0.5
    )
    ax2.set(ylim=(0, gb["patients"].max() * 2))
    plt.subplots(figsize=(15, 6))
    plt.gcf().autofmt_xdate()
    fname = GRAPHDIR / Path(f"{filedate}-cumulative.png")
    ax.figure.savefig(fname)
    return fname


def make_by_day(frame, filedate, unit):
    """Create a graph of new cases by earliest incident date"""
    gb = frame.groupby("Accurate_Episode_Date").agg(
        patients=pd.NamedAgg(column="Row_ID", aggfunc="size")
    )
    gb = gb.resample("D").last().fillna(0).reset_index()
    max_date = gb["Accurate_Episode_Date"].max().strftime("%Y-%m-%d")
    gb["rolling-avg"] = gb["patients"].rolling(WINDOW).mean()
    print(gb)
    ax = sns.lineplot(
        data=gb, x="Accurate_Episode_Date", y="patients", linestyle="--", linewidth=1
    )
    ax = sns.lineplot(data=gb, x="Accurate_Episode_Date", y="rolling-avg", linewidth=2)
    ax.set(
        ylabel="# of cases",
        xlabel="Date",
        title=f"{unit} Cases by Episode Date ({max_date})",
    )

    plt.legend(["daily", f"{WINDOW} day avg"])
    plt.gcf().autofmt_xdate()
    fname = GRAPHDIR / Path(f"{filedate}-by-date.png")
    ax.figure.savefig(fname)
    return fname


def process_health_unit(unit, filedate, frame):
    frame = frame.query(f"Reporting_PHU=='{unit}'").copy()
    frame["Accurate_Episode_Date"] = pd.to_datetime(
        frame["Accurate_Episode_Date"], format="%Y-%m-%d"
    )
    frame["byAge"] = frame["Age_Group"].astype(
        CategoricalDtype(AGE_CATEGORIES, ordered=True)
    )
    # reports ..
    fnames = []
    reports = (make_by_day, make_cumulative, make_by_age)
    for r in reports:
        fnames.append(
            r(frame, f"{unit.lower().replace(' ', '-')}-{filedate}", HEALTH_UNITS[unit])
        )
        plt.clf()
    return fnames


def process_reports(data, filedate):
    sns.set_theme()

    frame = pd.read_csv(data)

    return chain.from_iterable(
        process_health_unit(h, filedate, frame) for h in HEALTH_UNITS
    )


def main():
    data, filedate = get_data()
    process_reports(data, filedate)


if __name__ == "__main__":
    main()
