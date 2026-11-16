"""Collect news headlines about California domestic violence law from RSS/Atom feeds.

Reads the feed list in ../web/data/news_sources.json, keeps items the lexicon
says are DV-related, notes any bill numbers they mention (so the site can link
a story to the bill), and merges them into ../web/data/news.json.

Only headlines, links, source names and dates are stored, never article text.
A feed that fails is skipped; the others still update.

Usage:
    python news.py
    python news.py --sources my_feeds.json
"""

import argparse
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from flag import classify, load_lexicon

HERE = Path(__file__).parent
WEB_DATA = Path(os.environ.get("DV_WEB_DATA", HERE.parent / "web" / "data"))
UA = "dv-law-index/1.0 (+https://github.com/tusandia/ps158-reproduce)"
MAX_ITEMS = 300
MAX_AGE_DAYS = 365
BILL_RX = re.compile(r"\b(AB|SB)\s?-?(\d{1,4})\b")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def text_of(el):
    return html.unescape(re.sub(r"<[^>]+>", " ", "".join(el.itertext()) if el is not None else "")).strip()


def parse_date(s):
    if not s:
        return ""
    try:
        d = email.utils.parsedate_to_datetime(s)        # RSS: RFC 822
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))  # Atom: ISO 8601
        except ValueError:
            return ""
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc).isoformat(timespec="minutes")


def parse_feed(xml_bytes, feed_name):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.iter():
        if local(item.tag) not in ("item", "entry"):
            continue
        f = {local(c.tag): c for c in item}
        link = f.get("link")
        href = (link.get("href") or link.text or "").strip() if link is not None else ""
        source = f.get("source")
        out.append({
            "title": text_of(f.get("title")),
            "summary": text_of(f.get("description") or f.get("summary"))[:600],
            "link": href,
            "published": parse_date(text_of(f.get("pubDate") or f.get("published") or f.get("updated"))),
            "source": text_of(source) if source is not None else feed_name,
            "feed": feed_name,
        })
    return out


def relevant(item, lexicon):
    text = f"{item['title']}. {item['summary']}"
    r = classify(text, lexicon)
    if r["pred_label"] == "direct":
        return r
    if r["pred_label"] == "indirect" and re.search(r"california|sacramento|\bCA\b", text, re.I):
        return r
    return None


def norm_title(t):
    t = re.sub(r"\s+-\s+[^-]+$", "", t)  # Google News appends " - Source"
    return re.sub(r"\W+", " ", t).lower().strip()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sources", default=WEB_DATA / "news_sources.json")
    args = p.parse_args()

    lexicon = load_lexicon()
    sources = json.loads(Path(args.sources).read_text(encoding="utf-8"))
    path = WEB_DATA / "news.json"
    items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    seen = {i["link"] for i in items} | {norm_title(i["title"]) for i in items}
    added = 0
    for src in sources:
        try:
            req = urllib.request.Request(src["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                entries = parse_feed(r.read(), src["name"])
        except Exception as e:  # noqa: BLE001 - one bad feed must not stop the others
            print(f"{src['name']}: {e}, skipped", file=sys.stderr)
            continue
        for e in entries:
            if not e["title"] or not e["link"] or e["link"] in seen or norm_title(e["title"]) in seen:
                continue
            r = relevant(e, lexicon)
            if not r:
                continue
            e["label"] = r["pred_label"]
            e["areas"] = [a for a in r["pred_areas"].split(";") if a]
            e["bills"] = sorted({f"{k} {int(n)}" for k, n in BILL_RX.findall(e["title"] + " " + e["summary"])})
            e.pop("summary")
            items.append(e)
            seen |= {e["link"], norm_title(e["title"])}
            added += 1

    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=MAX_AGE_DAYS)).isoformat()
    items = [i for i in items if not i["published"] or i["published"] >= cutoff]
    items.sort(key=lambda i: i["published"], reverse=True)
    items = items[:MAX_ITEMS]
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{added} new headline(s); {len(items)} kept -> {path}")


if __name__ == "__main__":
    main()
