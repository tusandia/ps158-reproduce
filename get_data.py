"""Download Survey of Consumer Finances (SCF) summary extracts, 1989-2025, and
compute median family net worth by education of the family's reference person.

Source: Federal Reserve Board, SCF Summary Extract Public Data
(https://www.federalreserve.gov/econres/scfindex.htm). The Fed restates every
year's extract in dollars of the latest survey, currently 2025 dollars.

Education groups use EDCL, the education of the reference person:
    1 = no high school diploma, 2 = high school diploma or GED,
    3 = some college or associate degree, 4 = bachelor's degree or more.
"High school or less" pools EDCL 1 and 2.

Each family appears five times in the extract, once per imputation. As in the
Fed's published tables, statistics pool all five imputations, weighted by WGT;
this reproduces the Fed's Table 4 medians and means for each education group.

Outputs:
    data/raw/SCFP{year}.csv          raw extracts (not tracked by git)
    data/networth_by_education.csv   one row per survey year and group
"""

import io
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

YEARS = [1989, 1992, 1995, 1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025]
URL = "https://www.federalreserve.gov/econres/files/scfp{year}excel.zip"
DOLLAR_YEAR = 2025

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUT_FILE = DATA_DIR / "networth_by_education.csv"

COLUMNS = ["YY1", "Y1", "WGT", "EDCL", "NETWORTH"]
# The 1989 extract names the family and family-by-imputation IDs XX1 and X1.
ID_ALIASES = {"XX1": "YY1", "X1": "Y1"}
GROUPS = {
    "No high school diploma": [1],
    "High school diploma": [2],
    "High school or less": [1, 2],
    "Some college": [3],
    "Bachelor's degree or more": [4],
    "All families": [1, 2, 3, 4],
}


def download(year):
    """Fetch one year's CSV extract into data/raw, skipping it if already there."""
    path = RAW_DIR / f"SCFP{year}.csv"
    if path.exists():
        return path
    print(f"Downloading {year} ...")
    # The Fed's server rejects urllib's default User-Agent with a 403.
    req = Request(URL.format(year=year), headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        archive = zipfile.ZipFile(io.BytesIO(resp.read()))
    csvs = [n for n in archive.namelist() if n.lower().endswith(".csv")]
    if len(csvs) != 1:
        raise RuntimeError(f"{year}: expected one CSV in archive, found {csvs}")
    path.write_bytes(archive.read(csvs[0]))
    return path


def weighted_median(values, weights):
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cum = np.cumsum(weights)
    return values[np.searchsorted(cum, 0.5 * cum[-1])]


def summarize(df, year):
    total_weight = df["WGT"].sum()
    rows = []
    for group, codes in GROUPS.items():
        sub = df[df["EDCL"].isin(codes)]
        rows.append(
            {
                "year": year,
                "group": group,
                "median_networth": weighted_median(
                    sub["NETWORTH"].to_numpy(), sub["WGT"].to_numpy()
                ),
                "mean_networth": np.average(sub["NETWORTH"], weights=sub["WGT"]),
                "share_of_families": sub["WGT"].sum() / total_weight,
                "n_families": sub["YY1"].nunique(),
            }
        )
    return rows


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for year in YEARS:
        df = pd.read_csv(
            download(year),
            usecols=lambda c: c.upper() in COLUMNS or c.upper() in ID_ALIASES,
        )
        df.columns = df.columns.str.upper()
        df = df.rename(columns=ID_ALIASES)
        # Y1 = YY1 * 10 + imputation number (1-5).
        n_imp = (df["Y1"] - 10 * df["YY1"]).nunique()
        if n_imp != 5:
            raise RuntimeError(f"{year}: expected 5 imputations, found {n_imp}")
        rows += summarize(df, year)

    out = pd.DataFrame(rows)
    out["dollar_year"] = DOLLAR_YEAR
    out.to_csv(OUT_FILE, index=False, float_format="%.4f")
    print(f"Wrote {OUT_FILE}")

    wide = out.pivot(index="year", columns="group", values="median_networth")
    gap = wide["Bachelor's degree or more"] / wide["High school or less"]
    print(f"\nMedian net worth, thousands of {DOLLAR_YEAR} dollars:")
    print(
        pd.DataFrame(
            {
                "College": wide["Bachelor's degree or more"] / 1e3,
                "HS or less": wide["High school or less"] / 1e3,
                "Ratio": gap,
            }
        ).round(1)
    )


if __name__ == "__main__":
    main()
