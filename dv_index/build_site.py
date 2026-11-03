"""Build the bill explorer website from a flags file.

Usage:
    python build_site.py data/flags_2025.csv        # writes site/index.html

The page is a single self-contained HTML file (data embedded), built from
site/template.html. Re-run after re-flagging to refresh it.
"""

import argparse
import datetime as dt
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TEMPLATE = HERE / "site" / "template.html"
OUT = HERE / "site" / "index.html"


def excerpt(text, n=700):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0]
    return cut + " …"


def terms(matched):
    out = []
    for t in (matched or "").split("; "):
        name = re.sub(r"\s*\[[a-z_]+\]$", "", t).strip()
        kind = re.search(r"\[([a-z_]+)\]$", t)
        if not name or (kind and kind.group(1) == "population"):
            continue
        if name.startswith("re:"):
            name = "code section citation"
        name = name.rstrip("*")
        if name not in out:
            out.append(name)
    return out[:10]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("flags")
    p.add_argument("-o", "--output", default=OUT)
    args = p.parse_args()

    f = pd.read_csv(args.flags, dtype=str).fillna("")
    flagged = f[f["pred_label"].isin(["direct", "indirect"])]
    bills = [{
        "m": r.measure, "l": r.pred_label, "s": r.subject, "t": r.title,
        "a": [x for x in r.pred_areas.split(";") if x],
        "p": [x for x in r.populations.split(";") if x],
        "v": r.version_action, "d": r.action_date, "u": r.url,
        "x": excerpt(r.digest), "k": terms(r.matched_terms), "sc": float(r.score or 0),
    } for r in flagged.itertuples()]
    meta = {
        "total": len(f), "session": (f["session"].iloc[0] if len(f) else ""),
        "built": dt.date.today().isoformat(),
    }
    data = json.dumps({"meta": meta, "bills": bills}, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", data)
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"{len(bills)} bills -> {args.output}")


if __name__ == "__main__":
    main()
