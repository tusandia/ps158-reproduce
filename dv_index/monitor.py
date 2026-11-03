"""Repeatable update step: compare a fresh flags file with the running list of
flagged bills, report what is new or changed, and update the running list.

A bill is reported if it is flagged (direct or indirect) now and either
    - was not in the running list before (NEW), or
    - was there but its version changed (e.g. amended, passed, chaptered) (UPDATED).

Typical weekly run (the week of change files):
    python fetch_bills.py --daily Mon Tue Wed Thu Fri Sat
    python flag.py data/bills_daily.csv
    python monitor.py data/flags_daily.csv

Writes:
    data/tracked.csv                   running list of every flagged bill, latest version
    results/updates_YYYY-MM-DD.md      the digest to read or send to advocates
"""

import argparse
import datetime as dt
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TRACKED = HERE / "data" / "tracked.csv"


def compare(fresh, tracked):
    flagged = fresh[fresh["pred_label"].isin(["direct", "indirect"])].copy()
    if tracked is None or tracked.empty:
        flagged["change"] = "NEW"
        return flagged, flagged
    prev = tracked.set_index("bill_id")["version_id"]
    flagged["change"] = [
        "NEW" if b not in prev.index else ("UPDATED" if prev[b] != v else "")
        for b, v in zip(flagged["bill_id"], flagged["version_id"])
    ]
    changes = flagged[flagged["change"] != ""]
    merged = pd.concat([tracked[~tracked["bill_id"].isin(flagged["bill_id"])], flagged])
    return changes, merged


def digest_md(changes, date):
    lines = [f"# DV-relevant bill updates, {date}", ""]
    if changes.empty:
        return "\n".join(lines + ["No new or changed flagged bills."])
    for label in ("direct", "indirect"):
        sub = changes[changes["pred_label"] == label].sort_values("score", ascending=False)
        if sub.empty:
            continue
        lines += [f"## {label.capitalize()} ({len(sub)})", "",
                  "| Bill | Change | Status | Areas | Title |", "|---|---|---|---|---|"]
        for r in sub.itertuples():
            lines.append(f"| [{r.measure}]({r.url}) | {r.change} | {r.version_action} ({r.action_date}) | "
                         f"{r.pred_areas} | {str(r.title)[:160]} |")
        lines.append("")
    lines.append("_Flags are machine predictions from lexicon.csv; check each bill before relying on it._")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("flags")
    p.add_argument("--tracked", default=TRACKED)
    p.add_argument("--date", default=dt.date.today().isoformat())
    args = p.parse_args()

    fresh = pd.read_csv(args.flags, dtype=str).fillna("")
    fresh["score"] = pd.to_numeric(fresh["score"])
    tracked_path = Path(args.tracked)
    tracked = pd.read_csv(tracked_path, dtype=str).fillna("") if tracked_path.exists() else None
    changes, merged = compare(fresh, tracked)

    tracked_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(tracked_path, index=False)
    out = HERE / "results" / f"updates_{args.date}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(digest_md(changes, args.date), encoding="utf-8")
    print(f"{(changes['change'] == 'NEW').sum()} new, {(changes['change'] == 'UPDATED').sum()} updated -> {out}")


if __name__ == "__main__":
    main()
