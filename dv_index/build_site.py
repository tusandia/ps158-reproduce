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

from flag import load_lexicon

REALMS = ["immigrant_vawa", "women_gender", "faith", "language_access"]

# Hand-picked bills OUTSIDE the index that touch a realm in a way advocates may
# want to see. They are not DV laws and are shown separately on the page.
RELATED = {
    "faith": [
        ("AB 421", "Would bar local police from helping immigration enforcement within a mile of a place of worship, "
                   "among other sites. Matters to immigrant survivors who seek help through a mosque, temple, "
                   "gurdwara or church. Introduced only."),
        ("AB 1739", "Makes sexual exploitation of a congregation member by clergy a crime. About abuse by a "
                    "faith leader rather than a partner, so it falls outside the DV coding."),
    ],
}

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


def realm_snippets(text, lexicon, width=170):
    """For each realm, the first sentence-ish window of text that triggered it."""
    out = {}
    for t in lexicon:
        if t.kind != "population" or t.area not in REALMS or t.area in out:
            continue
        m = t.pattern.search(text)
        if m:
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            snip = re.sub(r"\s+", " ", text[a:b]).strip()
            out[t.area] = ("…" if a else "") + snip + ("…" if b < len(text) else "")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("flags")
    p.add_argument("-o", "--output", default=OUT)
    args = p.parse_args()

    f = pd.read_csv(args.flags, dtype=str).fillna("")
    flagged = f[f["pred_label"].isin(["direct", "indirect"])]
    lexicon = load_lexicon()
    bills = [{
        "m": r.measure, "l": r.pred_label, "s": r.subject, "t": r.title,
        "a": [x for x in r.pred_areas.split(";") if x],
        "p": [x for x in r.populations.split(";") if x],
        "v": r.version_action, "d": r.action_date, "u": r.url,
        "x": excerpt(r.digest), "k": terms(r.matched_terms), "sc": float(r.score or 0),
        "rs": realm_snippets(f"{r.title} {r.digest}", lexicon),
    } for r in flagged.itertuples()]
    related = {realm: [{"m": m, "note": note, "u": (f.loc[f["measure"] == m, "url"].iloc[0]
                                                    if (f["measure"] == m).any() else "")}
                       for m, note in items] for realm, items in RELATED.items()}
    meta = {
        "total": len(f), "session": (f["session"].iloc[0] if len(f) else ""),
        "built": dt.date.today().isoformat(),
    }
    data = json.dumps({"meta": meta, "bills": bills, "related": related}, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", data)
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"{len(bills)} bills -> {args.output}")


if __name__ == "__main__":
    main()
