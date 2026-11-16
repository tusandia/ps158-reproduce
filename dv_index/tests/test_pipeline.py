"""End-to-end checks on INVENTED bill summaries (not real bills) and a tiny
hand-made zip in the pubinfo layout. Run:  python tests/test_pipeline.py
"""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from fetch_bills import bills_from_zip, measure_from_bill_id  # noqa: E402
from flag import classify, flag_frame, load_lexicon  # noqa: E402
from monitor import compare  # noqa: E402

LEX = load_lexicon()

# (made-up text, expected label, an area that should be predicted)
CASES = [
    ("This bill would revise the Domestic Violence Prevention Act to define coercive control.", "direct", "courts"),
    ("Existing law requires a certifying entity to complete Form I-918 Supplement B within 30 days.", "indirect", "immigration"),
    ("This bill would allow a tenant who is a victim of stalking to terminate a lease early.", "indirect", "housing"),
    ("This bill would expand the Safe at Home program administered by the Secretary of State.", "indirect", "privacy"),
    ("This bill would require firearm relinquishment by persons subject to a protective order or civil restraining order.", "indirect", "firearms"),
    ("This bill would fund county substance abuse treatment and housing programs.", "none", None),
    ("This bill would change survivor benefits for retired firefighters.", "none", None),
    ("This bill would rename a state highway in Kern County.", "none", None),
]


def test_classify():
    for text, label, area in CASES:
        r = classify(text, LEX)
        assert r["pred_label"] == label, (text, r)
        if area:
            assert area in r["pred_areas"].split(";"), (text, r)


def test_measure_parse():
    assert measure_from_bill_id("202520260AB123") == ("2025-26", "AB 123")
    assert measure_from_bill_id("202520260SB7")[1] == "SB 7"


def make_zip(path):
    xml = ('<?xml version="1.0"?><caml:MeasureDoc xmlns:caml="http://lc.ca.gov/legalservices/schemas/caml.1#">'
           "<caml:Description><caml:Title>An act to amend Section 6320 of the Family Code, relating to domestic violence.</caml:Title>"
           "<caml:DigestText><p>Existing law, the Domestic Violence Prevention Act, authorizes a court to issue a protective order.</p></caml:DigestText>"
           "</caml:Description><caml:Bill><p>SECTION 1. Invented text.</p></caml:Bill></caml:MeasureDoc>")
    row = lambda vid, bid, num, date, action, lob: "\t".join(  # noqa: E731
        f"`{v}`" for v in [vid, bid, num, date, action, "", "Domestic violence", "MAJORITY", "NO", "NO",
                           "NO", "NO", "NO", "NO", lob, "Y", "", date])
    dat = "\n".join([
        row("20250AB99999INT", "202520260AB9999", "99", "2025-02-01 00:00:00", "Introduced", "BILL_VERSION_TBL_1.lob"),
        row("20250AB999998AMD", "202520260AB9999", "98", "2025-04-01 00:00:00", "Amended Assembly", "BILL_VERSION_TBL_2.lob"),
    ])
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("BILL_VERSION_TBL.dat", dat)
        z.writestr("BILL_VERSION_TBL_1.lob", xml.replace("6320", "6300"))
        z.writestr("BILL_VERSION_TBL_2.lob", xml)


def test_fetch_and_flag(tmp):
    z = tmp / "pubinfo_test.zip"
    make_zip(z)
    bills = bills_from_zip(z)
    assert len(bills) == 1
    b = bills.iloc[0]
    assert b.version_action == "Amended Assembly" and "6320" in b.title and b.measure == "AB 9999"
    assert flag_frame(bills, LEX, ["title", "subject", "digest"]).iloc[0].pred_label == "direct"


def test_sample_evaluate_monitor(tmp):
    df = pd.DataFrame({"bill_id": [f"B{i}" for i in range(len(CASES))],
                       "measure": [f"AB {i}" for i in range(len(CASES))],
                       "version_id": "v1", "version_action": "Introduced", "action_date": "2025-01-01",
                       "subject": "", "title": "", "digest": [c[0] for c in CASES], "url": "http://example.invalid"})
    flags = flag_frame(df, LEX, ["title", "subject", "digest"])
    fpath = tmp / "flags_test.csv"
    flags.to_csv(fpath, index=False)
    run = lambda *a: subprocess.run([sys.executable, *map(str, a)], cwd=HERE, check=True,  # noqa: E731
                                    capture_output=True, text=True)
    run("sample.py", fpath, "--n-direct", 5, "--n-indirect", 5, "--n-none", 5, "--outdir", tmp / "coding")
    sheet = pd.read_csv(tmp / "coding" / "coding_sheet.csv", dtype=str)
    assert "pred_label" not in sheet.columns  # blind
    gold = {f"B{i}": c[1] for i, c in enumerate(CASES)}
    gold["B5"] = "indirect"  # pretend the coder judged the substance-abuse housing bill relevant
    sheet["relevance"] = sheet["bill_id"].map(gold)
    sheet["areas"] = ""
    sheet.to_csv(tmp / "coding" / "coding_sheet.csv", index=False)
    run("evaluate.py", tmp / "coding" / "coding_sheet.csv", tmp / "coding" / "sample_key.csv",
        "--reps", 50, "-o", tmp / "eval.md")
    report = (tmp / "eval.md").read_text()
    assert "| Relevant (direct or indirect) | 1.00 | 0.83 |" in report, report  # 5 of 6 found
    assert "AB 5" in report  # the miss is listed
    run("evaluate.py", tmp / "coding" / "coding_sheet.csv", tmp / "coding" / "sample_key.csv",
        "--reps", 50, "-o", tmp / "eval2.md", "--flags", fpath)
    assert "| Relevant (direct or indirect) | 1.00 | 0.83 |" in (tmp / "eval2.md").read_text()

    changes, tracked = compare(flags, None)
    assert len(changes) == 5
    flags2 = flags.copy()
    flags2.loc[0, "version_id"] = "v2"
    changes2, _ = compare(flags2, tracked)
    assert changes2["change"].tolist() == ["UPDATED"]


def test_update_incremental(tmp):
    """Full build from one change file, then a later file amends the bill."""
    import json, os, zipfile as zf
    env = dict(os.environ, DV_WEB_DATA=str(tmp / "web"))
    z1 = tmp / "pubinfo_a.zip"
    make_zip(z1)
    run = lambda *a: subprocess.run([sys.executable, *map(str, a)], cwd=HERE, check=True,  # noqa: E731
                                    capture_output=True, text=True, env=env)
    run("update.py", "--full", "--zip", z1, "--session", 2025, "--today", "2026-01-01")
    bills = json.loads((tmp / "web" / "bills.json").read_text())
    assert [b["m"] for b in bills] == ["AB 9999"] and bills[0]["v"] == "Amended Assembly"
    assert json.loads((tmp / "web" / "updates.json").read_text()) == []   # first build logs nothing
    # same file again: nothing changes
    run("update.py", "--zip", z1, "--today", "2026-01-02")
    assert json.loads((tmp / "web" / "updates.json").read_text()) == []
    # a newer version arrives
    z2 = tmp / "pubinfo_b.zip"
    with zf.ZipFile(z1) as a, zf.ZipFile(z2, "w") as b:
        dat = a.read("BILL_VERSION_TBL.dat").decode().splitlines()[-1]
        dat = dat.replace("20250AB999998AMD", "20250AB999997AMD").replace("`98`", "`97`").replace(
            "2025-04-01", "2025-06-01").replace("Amended Assembly", "Amended Senate").replace("TBL_2.lob", "TBL_3.lob")
        b.writestr("BILL_VERSION_TBL.dat", dat)
        b.writestr("BILL_VERSION_TBL_3.lob", a.read("BILL_VERSION_TBL_2.lob"))
    run("update.py", "--zip", z2, "--today", "2026-01-03")
    log = json.loads((tmp / "web" / "updates.json").read_text())
    assert [(u["change"], u["m"], u["v"]) for u in log] == [("UPDATED", "AB 9999", "Amended Senate")], log
    meta = json.loads((tmp / "web" / "meta.json").read_text())
    assert meta["flagged"] == 1 and meta["updated"] == "2026-01-03"


def test_news_filter(tmp):
    import json, os
    feed = tmp / "feed.xml"
    feed.write_text("""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
      <item><title>Assembly passes AB 1753 on domestic violence restraining orders</title>
        <link>https://example.invalid/a</link><pubDate>Mon, 16 Nov 2026 08:00:00 GMT</pubDate>
        <source url="https://example.invalid">Example News</source></item>
      <item><title>New freeway interchange opens</title><link>https://example.invalid/b</link>
        <pubDate>Mon, 16 Nov 2026 09:00:00 GMT</pubDate></item>
    </channel></rss>""")
    sources = tmp / "sources.json"
    sources.write_text(json.dumps([{"name": "Test feed", "url": feed.as_uri()}]))
    env = dict(os.environ, DV_WEB_DATA=str(tmp / "web"))
    subprocess.run([sys.executable, "news.py", "--sources", str(sources)], cwd=HERE, check=True,
                   capture_output=True, text=True, env=env)
    items = json.loads((tmp / "web" / "news.json").read_text())
    assert [i["title"][:18] for i in items] == ["Assembly passes AB"], items
    assert items[0]["bills"] == ["AB 1753"] and items[0]["source"] == "Example News"


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_classify()
        test_measure_parse()
        test_fetch_and_flag(tmp)
        test_sample_evaluate_monitor(tmp)
        test_update_incremental(tmp)
        test_news_filter(tmp)
    print("all tests passed")
