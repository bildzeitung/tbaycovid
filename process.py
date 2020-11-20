#!/usr/bin/env python
"""
  Process Ontario provincial COVID daily data
"""

import csv

from collections import Counter, defaultdict, deque
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pylab as plt
import matplotlib.ticker as ticker
matplotlib.use('Agg')
import seaborn as sns
import pandas as pd

DATADIR = Path("data")
GRAPHDIR = Path("graphs")


def get_data():
  """ Choose latest data file
  """
  fnames = sorted(x for x in DATADIR.glob("*.csv"))
  latest = fnames[-1]
  date = "-".join(latest.name.split("-")[0:3])
  print(f"Latest file: {latest}")
  return open(latest), date


def is_tbay(line):
  return line["Reporting_PHU_City"] == "Thunder Bay"


def is_unresolved(line):
  return line["Outcome1"] == "Not Resolved" 


def make_by_age(lines, filedate):
  """ Active cases, grouped by age
  """

  # filter to active cases only
  lines = [x for x in lines if is_unresolved(x)]

  # aggregate
  ages = []
  dates = []
  for line in lines:
    ages.append(line["Age_Group"])
    dates.append(line["Accurate_Episode_Date"])
  c = Counter(ages)

  # move the columns into the right order
  k = deque(sorted(c))
  k.rotate(1)

  # make the graph
  s = pd.DataFrame(c, index=["patients"], columns=k)
  print(s)
  ax = sns.barplot(data=s, palette="Blues_d")
  ax.set(xlabel="Age Group", ylabel="Active Cases", title=f"T Bay Active Cases by Age Group ({max(dates)})")
  ax.figure.savefig(GRAPHDIR / Path(f"{filedate}-by-age.png"))


def make_cumulative(lines, filedate):
  """ Create a cumulative graph of cases over time
  """
  d = defaultdict(int)
  for line in lines:
    d[line["Accurate_Episode_Date"]] += 1
  current = datetime.strptime(sorted(d.keys())[0], "%Y-%m-%d")
  end = datetime.strptime(sorted(d.keys())[-1], "%Y-%m-%d")
  total = 0
  data = []
  all_dates = []
  while current <= end:
    cstr = current.strftime("%Y-%m-%d")
    all_dates.append(cstr)
    total += d[cstr]
    data.append([cstr, total])
    current = current + timedelta(days=1)
  
  s = pd.DataFrame(data, columns=["date", "cases"])
  print(s)
  ax = sns.lineplot(data=s, x="date", y="cases", palette="Blues_d")
  ax.set(xlabel="Date", ylabel="Cases", title=f"T Bay Cumulative Cases Since Tracking Began ({data[-1][0]})")
  ax.xaxis.set_major_locator(ticker.MultipleLocator(14))
  plt.xticks(rotation=90)
  ax.figure.savefig(GRAPHDIR / Path(f"{filedate}-cumulative.png"))


def make_by_day(lines, filedate):
  """ Create a graph of new cases by earliest incident date
  """
  d = defaultdict(int)
  for line in lines:
    d[line["Accurate_Episode_Date"]] += 1
  current = datetime.strptime(sorted(d.keys())[0], "%Y-%m-%d")
  end = datetime.strptime(sorted(d.keys())[-1], "%Y-%m-%d")
  data = []
  all_dates = []
  while current <= end:
    cstr = current.strftime("%Y-%m-%d")
    all_dates.append(cstr)
    data.append([cstr, d[cstr]])
    current = current + timedelta(days=1)
  s = pd.DataFrame(data, columns=["date", "cases"])
  print(s)
  ax = sns.lineplot(data=s, x="date", y="cases", palette="Blues_d")
  ax.set(xlabel="Date", ylabel="Cases", title=f"T Bay Cases by Episode Date ({data[-1][0]})")
  ax.xaxis.set_major_locator(ticker.MultipleLocator(14))
  plt.xticks(rotation=90)
  ax.figure.savefig(GRAPHDIR / Path(f"{filedate}-by-date.png"))


def main():
  data, filedate = get_data()

  # read and filter for Thunder Bay only
  r = csv.DictReader(data)
  lines = [line for line in r if is_tbay(line)]

  # reports ..
  reports = (make_by_day, make_cumulative, make_by_age)
  for r in reports:
    r(lines, filedate)
    plt.clf()


if __name__ == "__main__":
  main()