"""Download California bills from the Legislature's public bulk data
(https://downloads.leginfo.legislature.ca.gov/) and write one row per bill,
using each bill's most recent version.

Two kinds of download:
    --session 2025   pubinfo_2025.zip: every bill of the 2025-26 session (large).
    --daily Mon Tue  pubinfo_Mon.zip etc.: only records changed on that weekday
                     (small; the server keeps the last 7 days). Use for the
                     weekly update step (see monitor.py). Not to be confused
                     with pubinfo_daily_Mon.zip, a full 1 GB snapshot.

The zips hold MySQL dump tables (.dat: tab-separated, fields wrapped in
backticks). Bill text sits in separate .lob files named by BILL_VERSION_TBL's
bill_xml column. From each version's XML we keep the title and the
Legislative Counsel's Digest (a plain-language summary that names every code
section the bill changes); --full-text also keeps the full bill text.

NOTE: written against the documented pubinfo layout but not yet run on a real
download, because the build environment could not reach leginfo. If a column
looks shifted, check BILL_VERSION_COLUMNS against the capublic.sql schema
that ships on the downloads page.

Output: data/bills_{session or "daily"}.csv with columns
    bill_id, measure, session, version_id, version_action, action_date,
    subject, title, digest, [full_text], url

Usage:
    python fetch_bills.py --session 2025
    python fetch_bills.py --daily Mon Tue Wed Thu Fri Sat   # this week's changes
    python fetch_bills.py --zip path/to/pubinfo_2025.zip   # already downloaded
"""

import argparse
import csv
import io
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

BASE = "https://downloads.leginfo.legislature.ca.gov/"
BILL_URL = "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id={}"
HERE = Path(__file__).parent
RAW_DIR = HERE / "data" / "raw"

# Column order of BILL_VERSION_TBL in capublic.sql.
BILL_VERSION_COLUMNS = [
    "bill_version_id", "bill_id", "version_num", "bill_version_action_date",
    "bill_version_action", "request_num", "subject", "vote_required",
    "appropriation", "fiscal_committee", "local_program", "substantive_changes",
    "urgency", "taxlevy", "bill_xml", "active_flg", "trans_uid", "trans_update",
]

csv.field_size_limit(sys.maxsize)


def download(name, fresh=False):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / name
    if dest.exists() and not fresh:
        print(f"using cached {dest}")
        return dest
    url = BASE + name
    print(f"downloading {url} ...")
    req = Request(url, headers={"User-Agent": "dv-index-research-script"})
    tmp = dest.with_suffix(".part")
    with urlopen(req) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.rename(dest)
    return dest


def members_by_basename(zf):
    return {Path(n).name.lower(): n for n in zf.namelist() if not n.endswith("/")}


def read_dat(zf, member, columns):
    text = zf.read(member).decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text), delimiter="\t", quotechar="`")
    rows = []
    for fields in reader:
        if not fields:
            continue
        fields = [None if f == "NULL" else f for f in fields]
        fields = (fields + [None] * len(columns))[:len(columns)]
        rows.append(dict(zip(columns, fields)))
    return pd.DataFrame(rows, columns=columns)


def local(tag):
    return tag.rsplit("}", 1)[-1]


def collapse(s):
    return re.sub(r"\s+", " ", s or "").strip()


def parse_bill_xml(xml_bytes):
    """Return (title, digest, full_text) from one bill version's XML."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return "", "", ""
    title = digest = full = ""
    for el in root.iter():
        name = local(el.tag)
        if name == "Title" and not title:
            title = collapse("".join(el.itertext()))
        elif name == "DigestText" and not digest:
            digest = collapse(" ".join(el.itertext()))
        elif name == "Bill" and not full:
            full = collapse(" ".join(el.itertext()))
    return title, digest, full


def measure_from_bill_id(bill_id):
    """'202520260AB123' -> ('2025-26', 'AB 123')."""
    m = re.match(r"(\d{4})(\d{4})(\d)([A-Z]+)(\d+)$", bill_id or "")
    if not m:
        return "", bill_id or ""
    start, end, special, kind, num = m.groups()
    session = f"{start}-{end[2:]}" + (f" Extraordinary Session {special}" if special != "0" else "")
    return session, f"{kind} {int(num)}"


def bills_from_zip(path, full_text=False):
    with zipfile.ZipFile(path) as zf:
        names = members_by_basename(zf)
        member = names.get("bill_version_tbl.dat")
        if member is None:  # normal for a daily change file with no new bill versions
            print(f"{path.name}: no bill versions changed")
            return pd.DataFrame()
        versions = read_dat(zf, member, BILL_VERSION_COLUMNS)
        if versions.empty:
            return pd.DataFrame()

        # Latest version per bill: latest action date; on ties the lower
        # version_num (versions count down from 99 = as introduced).
        versions["date_"] = pd.to_datetime(versions["bill_version_action_date"], errors="coerce")
        versions["num_"] = pd.to_numeric(versions["version_num"], errors="coerce")
        latest = (versions.sort_values(["bill_id", "date_", "num_"], ascending=[True, False, True])
                  .drop_duplicates("bill_id"))

        out = []
        for row in latest.itertuples():
            title = digest = full = ""
            lob = names.get(Path(row.bill_xml or "").name.lower())
            if lob:
                title, digest, full = parse_bill_xml(zf.read(lob))
            session, measure = measure_from_bill_id(row.bill_id)
            rec = {
                "bill_id": row.bill_id, "measure": measure, "session": session,
                "version_id": row.bill_version_id, "version_action": row.bill_version_action,
                "action_date": row.date_.date().isoformat() if pd.notna(row.date_) else "",
                "subject": collapse(row.subject), "title": title, "digest": digest,
                "url": BILL_URL.format(row.bill_id),
            }
            if full_text:
                rec["full_text"] = full
            out.append(rec)
    return pd.DataFrame(out)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--session", type=int, help="first year of the session, e.g. 2025")
    src.add_argument("--daily", nargs="+", choices=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    src.add_argument("--zip", help="a pubinfo zip already on disk")
    p.add_argument("--full-text", action="store_true", help="also keep full bill text (big)")
    p.add_argument("-o", "--output")
    args = p.parse_args()

    if args.zip:
        paths, tag = [Path(args.zip)], Path(args.zip).stem.replace("pubinfo_", "")
    elif args.session:
        paths, tag = [download(f"pubinfo_{args.session}.zip")], str(args.session)
    else:
        # Change files are overwritten weekly, so never reuse a cached copy.
        paths, tag = [download(f"pubinfo_{d}.zip", fresh=True) for d in args.daily], "daily"

    frames = [bills_from_zip(p, args.full_text) for p in paths]
    bills = pd.concat([f for f in frames if not f.empty] or [pd.DataFrame()], ignore_index=True)
    if not bills.empty:  # same bill changed on several days: keep the latest version
        bills = bills.sort_values("action_date").drop_duplicates("bill_id", keep="last")
    out = Path(args.output) if args.output else HERE / "data" / f"bills_{tag}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    bills.to_csv(out, index=False)
    print(f"{len(bills)} bills -> {out}")


if __name__ == "__main__":
    main()
