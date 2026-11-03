# California DV law index: flagging pipeline

POLISCI 158 final project (Sadia Nahar Orpa). The goal is to find California
bills that are **directly** about domestic violence, or that **indirectly**
but materially affect DV survivors (immigration, housing, custody, firearms,
benefits, language access, courts, privacy and more), and to measure how well
a keyword-and-theme tool finds them compared with hand coding.

```
fetch_bills.py  ->  flag.py  ->  sample.py  ->  (you hand-code)  ->  evaluate.py
                                     \-> monitor.py  (weekly update of new/changed bills)
```

| File | What it does |
|---|---|
| `CODEBOOK.md` | The coding scheme: `direct` / `indirect` / `none`, impact-area and population tags, procedure, and what the index can't capture. |
| `lexicon.csv` | The tool's term list. Edit it in Excel or Sheets; no code changes needed. |
| `fetch_bills.py` | Downloads the Legislature's bulk data and writes one row per bill (latest version): title, subject, Legislative Counsel's Digest, link. |
| `flag.py` | Applies the lexicon and predicts a label, impact areas, population tags, and the matched terms behind each prediction. |
| `sample.py` | Draws a stratified sample to hand-code. It includes unflagged bills, so recall can be measured, and the coding sheet hides predictions. |
| `evaluate.py` | Computes precision, recall and F1 (sample and population-weighted, with bootstrap CIs), a confusion table, per-area scores, every miss and false alarm, and optionally intra-coder kappa. |
| `monitor.py` | Weekly step: reports newly flagged bills, and flagged bills with a new version, as a markdown digest. |

## Data

Source: [downloads.leginfo.legislature.ca.gov](https://downloads.leginfo.legislature.ca.gov/),
the Legislature's official bulk data:
- `pubinfo_2025.zip` (1.2 GB) holds the full 2025–26 session.
- `pubinfo_Mon.zip` … `pubinfo_Sat.zip` are small files of each weekday's changes; the server keeps the last 7 days.

Table layouts are in `pubinfo_load.zip` (`capublic.sql`). The bill page
website (leginfo.legislature.ca.gov) blocks scripts with a Cloudflare check,
so the pipeline uses only the bulk downloads.

The tool reads the **title, subject and Legislative Counsel's Digest** of each
bill's latest version. The digest is a plain-language summary that names every
code section the bill touches, which is how the lexicon catches indirect laws
by citation (e.g. Civ. Code §1946.7, lease termination for victims).
`--full-text` keeps the whole bill if you want to compare.

## First run: 2025–26 session (downloaded 2026-11-03)

- **4,262 bills** (2,811 AB, 1,451 SB). Every bill has a title and digest.
- The tool predicts **59 direct, 73 indirect, 4,130 none**.
- The 132 flagged bills are in `results/flagged_2025.csv`, with links and matched terms.
- The coding sheet is drawn and ready: `coding/coding_sheet.csv` (292 bills).

| Stratum | Bills | Sampled | Weight |
|---|---|---|---|
| direct | 59 | 59 (all) | 1 |
| indirect | 73 | 73 (all) | 1 |
| none | 4,130 | 160 | 25.8 |

Each relevant bill you find in the `none` stratum stands for about 26 missed
bills, which is why recall is the uncertain number. If time allows, code more
`none` rows: draw a second sample of new bills rather than re-running
`sample.py` with the same seed.

**How the lexicon got to this version.** Before any hand-coding, I read the
flag lists by eye and made these changes:
- Dropped catch-all terms: `grant*`, `employee*`, `employer*`, bare `custody`, `safety plan`.
- Required anchor weight ≥ 2 for `indirect`.
- Down-weighted `protective order` and `restraining order`, so workplace-violence orders no longer count as direct.
- Added DVPA citation rules (Fam. Code §§6200–6409) and forced/coerced marriage.

This raised the share of plausible bills among the indirect flags from roughly
a third to most of the 73. Report it as lexicon development. The precision and
recall numbers should come only from your coding.

## Running it

Requires Python 3 with pandas and numpy (`pip install -r ../requirements.txt`).

```bash
python fetch_bills.py --session 2025
```

```bash
python flag.py data/bills_2025.csv
```

```bash
python sample.py data/flags_2025.csv --n-direct 60 --n-indirect 80 --n-none 160
```

Then fill in `relevance`, `areas`, `populations` and `notes` in
`coding/coding_sheet.csv` by following `CODEBOOK.md`. Rows you leave blank are skipped.

```bash
python evaluate.py coding/coding_sheet.csv coding/sample_key.csv
```

Weekly update:

```bash
python fetch_bills.py --daily Mon Tue Wed Thu Fri Sat && python flag.py data/bills_daily.csv && python monitor.py data/flags_daily.csv
```

Tests (invented bill text, not real bills):

```bash
python tests/test_pipeline.py
```

## Method notes

- **Why stratify.** Very few bills are DV-relevant, so a simple random sample
  would contain almost no positives. A sample made only of flagged bills can't
  measure recall. Sampling from each predicted label, then weighting each
  stratum back to its true size, gives unbiased estimates of both precision
  and recall. The `none` stratum is the hard one: indirect laws are rare
  there, so recall intervals stay wide unless that stratum is large.
- **Blind coding.** The coding sheet is shuffled and shows no predictions.
- **Iterating the lexicon.** `evaluate.py` lists every miss with your notes.
  Add terms to `lexicon.csv`, re-run `flag.py`, and report how many terms
  were added after seeing the gold set. Better still, hold out part of the
  coded sample, or code a fresh sample for the final numbers, so the reported
  recall isn't tuned to the same bills.
- **Statutes.** The flagger works on any CSV with an id column and text
  columns (`--text-cols`), so code sections can be run through the same lexicon.

## Website

`site/index.html` is a self-contained, searchable page of every flagged bill.
You can filter it by direct or indirect, impact area, status and group
reached, and each bill links to its leginfo page. Rebuild it after
re-flagging:

```bash
python build_site.py data/flags_2025.csv
```

It's a single HTML file with the data built in, so any static host can serve it
(for example GitHub Pages, or just open it in a browser).
