"""Daily update of the website's data from the Legislature's bulk downloads.

Writes everything the Next.js site in ../web reads, into ../web/data/:
    bills.json      every flagged bill (direct or indirect), latest version
    updates.json    log of what changed: NEW, UPDATED, REMOVED (newest first)
    gaps.json       how many bills mention each documented gap
    meta.json       counts, sessions, when it last ran
    state.json      every bill seen: version id + which gaps it mentions
    federal.json, lexicon.json, codebook.html, related.json   reference data

Two modes:
    python update.py            incremental: reads this week's small change files
                                (pubinfo_Mon.zip ... pubinfo_Sun.zip) and re-flags
                                only bills whose version changed. Safe to run
                                repeatedly; nothing happens if nothing changed.
    python update.py --full     rebuild from the whole session file
                                (pubinfo_YYYY.zip, about 1.2 GB). Run weekly to
                                self-heal, and whenever the lexicon changes.

Source: https://downloads.leginfo.legislature.ca.gov/ (official, public).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
from pathlib import Path

import pandas as pd

from build_site import (GAPS, RELATED, bill_record, codebook_html, federal_rows,
                        lexicon_rows)
from fetch_bills import bills_from_zip, download
from flag import flag_frame, load_lexicon

HERE = Path(__file__).parent
WEB_DATA = Path(os.environ.get("DV_WEB_DATA", HERE.parent / "web" / "data"))
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TEXT_COLS = ["title", "subject", "digest"]
GAP_RX = [re.compile(rx, re.I) for _, rx, _ in GAPS]
MAX_UPDATES = 1000


def current_session(today=None):
    """First year of the session in progress. A new two-year session opens the
    first Monday of December of even years, so December 2026 belongs to 2027-28."""
    today = today or dt.date.today()
    y = today.year
    if y % 2 == 0:
        return y + 1 if today.month == 12 else y - 1
    return y


def read_json(name, default):
    path = WEB_DATA / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(name, obj):
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def gap_hits(row):
    text = f"{row['title']} {row['subject']} {row['digest']}"
    return [i for i, rx in enumerate(GAP_RX) if rx.search(text)]


def fetch_changes(zips):
    frames = [bills_from_zip(z) for z in zips]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame()
    bills = pd.concat(frames, ignore_index=True)
    return bills.sort_values("action_date").drop_duplicates("bill_id", keep="last")


def apply(bills, state, flagged, today, lexicon, full):
    """Re-flag changed bills (all bills when `full`); update state and the flagged
    set in place. Returns change-log entries."""
    log = []
    if full:
        changed = bills
    else:
        changed = bills[[state.get(b, {}).get("v") != v for b, v in zip(bills["bill_id"], bills["version_id"])]]
    if changed.empty:
        return log
    scored = flag_frame(changed.fillna(""), lexicon, TEXT_COLS)
    for r in scored.fillna("").to_dict("records"):
        bid = r["bill_id"]
        state[bid] = {"v": r["version_id"], "g": gap_hits(r)}
        was = flagged.get(bid)
        if r["pred_label"] in ("direct", "indirect"):
            rec = bill_record(r, lexicon)
            flagged[bid] = rec
            if was is None:
                change = "NEW"
            elif was.get("vid") != rec["vid"] or was.get("l") != rec["l"]:
                change = "UPDATED"
            else:
                change = None
            if change:
                log.append({"date": today, "change": change, "id": bid, "m": rec["m"], "l": rec["l"],
                            "s": rec["s"], "v": rec["v"], "u": rec["u"]})
        elif was is not None:
            flagged.pop(bid)
            log.append({"date": today, "change": "REMOVED", "id": bid, "m": was["m"], "l": "none",
                        "s": was["s"], "v": r["version_action"], "u": was["u"]})
    return log


def write_reference():
    write_json("federal.json", federal_rows())
    write_json("lexicon.json", lexicon_rows())
    write_json("related.json", {k: [{"m": m, "note": n} for m, n in v] for k, v in RELATED.items()})
    (WEB_DATA / "codebook.html").write_text(codebook_html(), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--full", action="store_true", help="rebuild from the whole session file")
    p.add_argument("--session", type=int, default=None, help="first year of the session (default: current)")
    p.add_argument("--zip", nargs="+", help="use these pubinfo zips instead of downloading (for testing)")
    p.add_argument("--today", default=dt.date.today().isoformat())
    args = p.parse_args()

    session = args.session or current_session(dt.date.fromisoformat(args.today))
    lexicon = load_lexicon()
    state = {} if args.full else read_json("state.json", {})
    flagged = {b["id"]: b for b in read_json("bills.json", [])}
    old_flagged = dict(flagged)
    if args.full:
        flagged = {}
    updates = read_json("updates.json", [])

    if args.zip:
        zips = [Path(z) for z in args.zip]
    elif args.full:
        zips = [download(f"pubinfo_{session}.zip")]
    else:
        zips = []
        for day in DAYS:
            try:
                zips.append(download(f"pubinfo_{day}.zip", fresh=True))
            except (urllib.error.URLError, OSError) as e:
                print(f"pubinfo_{day}.zip: {e}, skipped", file=sys.stderr)
        if not zips:
            sys.exit("could not download any change file; is downloads.leginfo.legislature.ca.gov reachable?")

    bills = fetch_changes(zips)
    print(f"{len(bills)} bill versions in {len(zips)} file(s)")
    log = apply(bills, state, flagged, args.today, lexicon, args.full)

    if args.full:  # log against what the site showed before (nothing, on a first build)
        log = []
        for bid, rec in flagged.items():
            was = old_flagged.get(bid)
            if was is None and old_flagged:
                log.append({"date": args.today, "change": "NEW", "id": bid, "m": rec["m"], "l": rec["l"],
                            "s": rec["s"], "v": rec["v"], "u": rec["u"]})
            elif was is not None and (was.get("vid") != rec["vid"] or was.get("l") != rec["l"]):
                log.append({"date": args.today, "change": "UPDATED", "id": bid, "m": rec["m"], "l": rec["l"],
                            "s": rec["s"], "v": rec["v"], "u": rec["u"]})
        for bid, was in old_flagged.items():
            if bid not in flagged:
                log.append({"date": args.today, "change": "REMOVED", "id": bid, "m": was["m"], "l": "none",
                            "s": was["s"], "v": "", "u": was["u"]})

    updates = (log + updates)[:MAX_UPDATES]
    ordered = sorted(flagged.values(), key=lambda b: (b["l"] != "direct", -b["sc"], b["m"]))
    gaps = [{"issue": name, "src": src, "n": sum(1 for s in state.values() if i in s.get("g", []))}
            for i, (name, _, src) in enumerate(GAPS)]
    sessions = sorted({b["session"] for b in ordered if b.get("session")})
    meta = read_json("meta.json", {})
    meta.update({
        "updated": args.today, "total": len(state), "flagged": len(ordered),
        "direct": sum(b["l"] == "direct" for b in ordered),
        "became_law": sum(b["v"] == "Chaptered" for b in ordered),
        "sessions": sessions, "current_session": f"{session}-{str(session + 1)[2:]}",
    })
    if args.full:
        meta["last_full_refresh"] = args.today

    write_json("bills.json", ordered)
    write_json("updates.json", updates)
    write_json("gaps.json", gaps)
    write_json("meta.json", meta)
    write_json("state.json", state)
    write_reference()
    print(f"{len(ordered)} flagged bills; {len(log)} change(s) logged -> {WEB_DATA}")


if __name__ == "__main__":
    main()
